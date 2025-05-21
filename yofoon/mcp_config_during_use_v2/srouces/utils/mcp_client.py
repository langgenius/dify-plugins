import json
import logging
import time
from abc import ABC, abstractmethod
from queue import Queue, Empty
from threading import Event, Thread
from typing import Any, Optional
from urllib.parse import urljoin, urlparse

import httpx
from httpx_sse import connect_sse, EventSource


def remove_request_params(url: str) -> str:
    return urljoin(url, urlparse(url).path)


class McpClientBase(ABC):
    """Interface for MCP client."""

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def initialize(self):
        raise NotImplementedError

    @abstractmethod
    def list_tools(self):
        raise NotImplementedError

    @abstractmethod
    def call_tool(self, tool_name: str, tool_args: dict):
        raise NotImplementedError


class McpClient(McpClientBase):
    def __init__(self, url: str,
                 headers: dict[str, Any] | None = None,
                 timeout: float = 60,
                 sse_read_timeout: float = 60 * 5,
                 max_retries: int = 3,
                 retry_interval: float = 2.0,
                 ):
        self.url = url
        self.timeout = timeout
        self.sse_read_timeout = sse_read_timeout
        self.max_retries = max_retries
        self.retry_interval = retry_interval
        self.endpoint_url = None
        self.client = httpx.Client(headers=headers)
        self._request_id = 0
        self.message_queue = Queue()
        self.response_ready = Event()
        self.should_stop = Event()
        self._listen_thread = None
        self._connected = Event()
        self.connect()

    def _listen_messages(self) -> None:
        logging.info(f"Connecting to SSE endpoint: {remove_request_params(self.url)}")
        retry_count = 0
        
        while not self.should_stop.is_set() and retry_count <= self.max_retries:
            try:
                with connect_sse(
                        client=self.client,
                        method="GET",
                        url=self.url,
                        timeout=httpx.Timeout(self.timeout, read=self.sse_read_timeout),
                ) as event_source:
                    event_source.response.raise_for_status()
                    logging.debug("SSE connection established")
                    retry_count = 0
                    
                    for sse in event_source.iter_sse():
                        if self.should_stop.is_set():
                            logging.info("Stopping SSE listener due to stop signal")
                            break
                            
                        logging.debug(f"Received SSE event: {sse.event}")
                        match sse.event:
                            case "endpoint":
                                self.endpoint_url = urljoin(self.url, sse.data)
                                logging.info(f"Received endpoint URL: {self.endpoint_url}")
                                self._connected.set()
                                url_parsed = urlparse(self.url)
                                endpoint_parsed = urlparse(self.endpoint_url)
                                if (url_parsed.netloc != endpoint_parsed.netloc
                                        or url_parsed.scheme != endpoint_parsed.scheme):
                                    error_msg = f"Endpoint origin does not match connection origin: {self.endpoint_url}"
                                    logging.error(error_msg)
                                    raise ValueError(error_msg)
                            case "message":
                                message = json.loads(sse.data)
                                logging.debug(f"Received server message: {message}")
                                self.message_queue.put(message)
                                self.response_ready.set()
                            case _:
                                logging.warning(f"Unknown SSE event: {sse.event}")
                                
            except httpx.ReadError as e:
                if self.should_stop.is_set():
                    logging.debug(f"Ignoring SSE connection read error due to stop signal: {str(e)}")
                    break
                
                logging.warning(f"SSE connection read error: {str(e)}")
                if retry_count < self.max_retries:
                    retry_count += 1
                    logging.info(f"Retrying SSE connection ({retry_count}/{self.max_retries}) in {self.retry_interval} seconds...")
                    time.sleep(self.retry_interval)
                else:
                    logging.error(f"Max retries ({self.max_retries}) exceeded for SSE connection")
                    break
            except Exception as e:
                logging.error(f"Error in SSE connection: {str(e)}")
                if retry_count < self.max_retries:
                    retry_count += 1
                    logging.info(f"Retrying SSE connection ({retry_count}/{self.max_retries}) in {self.retry_interval} seconds...")
                    time.sleep(self.retry_interval)
                else:
                    logging.error(f"Max retries ({self.max_retries}) exceeded for SSE connection")
                    break

    def send_message(self, data: dict):
        if not self.endpoint_url:
            raise RuntimeError("please call connect() first")
        logging.debug(f"Sending client message: {data}")
        response = self.client.post(
            url=self.endpoint_url,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=self.timeout
        )
        response.raise_for_status()
        logging.debug(f"Client message sent successfully: {response.status_code}")
        if "id" in data:
            message_id = data["id"]
            while True:
                self.response_ready.wait()
                self.response_ready.clear()
                try:
                    while True:
                        message = self.message_queue.get_nowait()
                        if "id" in message and message["id"] == message_id:
                            self._request_id += 1
                            return message
                        self.message_queue.put(message)
                except Empty:
                    pass
        return {}

    def connect(self) -> None:
        self._listen_thread = Thread(target=self._listen_messages, daemon=True)
        self._listen_thread.start()
        if not self._connected.wait(timeout=self.timeout):
            raise TimeoutError("MCP Server connection timeout!")

    def close(self) -> None:
        self.should_stop.set()
        self.client.close()
        if self._listen_thread and self._listen_thread.is_alive():
            self._listen_thread.join(timeout=10)

    def initialize(self):
        init_data = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "mcp",
                    "version": "0.1.0"
                }
            }
        }
        self.send_message(init_data)
        notify_data = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        self.send_message(notify_data)

    def list_tools(self):
        tools_data = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": "tools/list",
            "params": {}
        }
        return self.send_message(tools_data).get("result", {}).get("tools", [])

    def call_tool(self, tool_name: str, tool_args: dict):
        call_data = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": tool_args
            }
        }
        return self.send_message(call_data).get("result", {}).get("content", [])


class McpStreamableHttpClient(McpClientBase):
    """
    Streamable HTTP transport MCP client.
    """

    def __init__(self, url: str,
                 headers: dict[str, Any] | None = None,
                 timeout: float = 60,
                 ):
        self.url = url
        self.timeout = timeout
        self.client = httpx.Client(headers=headers)
        self.session_id = None
        self._request_id = 0

    def close(self) -> None:
        try:
            self.client.close()
        except Exception as e:
            raise Exception(f"MCP Server connection close failed: {str(e)}")

    def send_message(self, data: dict):
        headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        logging.debug(f"Sending client message: {data}")
        response = self.client.post(
            url=self.url,
            json=data,
            headers=headers,
            timeout=self.timeout
        )
        self.session_id = response.headers.get("mcp-session-id", None)
        content_type = response.headers.get("content-type", "None")
        if content_type == "text/event-stream":
            for sse in EventSource(response).iter_sse():
                if sse.event != "message":
                    raise Exception(f"Unknown Server-Sent Event: {sse.event}")
                return json.loads(sse.data)
        elif content_type == "application/json":
            return response.json() if response.content else {}
        else:
            raise Exception(f"Unsupported Content-Type: {content_type}")

    def initialize(self):
        init_data = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "MCP Streamable HTTP Client",
                    "version": "0.1.0"
                }
            }
        }
        response = self.send_message(init_data)
        self._request_id += 1
        if "error" in response:
            raise Exception(f"MCP Server initialize error: {response['error']}")
        notify_data = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        response = self.send_message(notify_data)
        if "error" in response:
            raise Exception(f"MCP Server notifications/initialized error: {response['error']}")

    def list_tools(self):
        tools_data = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": "tools/list",
            "params": {}
        }
        response = self.send_message(tools_data)
        self._request_id += 1
        if "error" in response:
            raise Exception(f"MCP Server tools/list error: {response['error']}")
        return response.get("result", {}).get("tools", [])

    def call_tool(self, tool_name: str, tool_args: dict):
        call_data = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": tool_args
            }
        }
        response = self.send_message(call_data)
        self._request_id += 1
        if "error" in response:
            raise Exception(f"MCP Server tools/call error: {response['error']}")
        return response.get("result", {}).get("content", [])


class McpClientsUtil:

    @staticmethod
    def create_client(url: str, 
                    transport: str = "sse",
                    headers: Optional[dict] = None, 
                    timeout: float = 60, 
                    sse_read_timeout: float = 300) -> McpClientBase:
        """Create MCP client based on transport type"""
        if transport == "streamable_http":
            return McpStreamableHttpClient(
                url=url,
                headers=headers,
                timeout=timeout,
            )
        else:  # default to SSE
            return McpClient(
                url=url,
                headers=headers,
                timeout=timeout,
                sse_read_timeout=sse_read_timeout
            )

    @staticmethod
    def fetch_tools(server_url: str, 
                    transport: str = "sse",
                    headers: Optional[dict] = None, 
                    timeout: float = 60, 
                    sse_read_timeout: float = 300) -> list[dict]:
        """fetch tools from mcp server"""
        client = McpClientsUtil.create_client(
            url=server_url,
            transport=transport,
            headers=headers,
            timeout=timeout,
            sse_read_timeout=sse_read_timeout
        )
        try:
            client.initialize()
            return client.list_tools()
        finally:
            client.close()

    @staticmethod
    def execute_tool(server_url: str,
                     tool_name: str, 
                     tool_args: dict[str, Any],
                     transport: str = "sse",
                     headers: Optional[dict] = None, 
                     timeout: float = 60, 
                     sse_read_timeout: float = 300) -> str:
        """execute tool on mcp server"""
        client = McpClientsUtil.create_client(
            url=server_url,
            transport=transport,
            headers=headers,
            timeout=timeout,
            sse_read_timeout=sse_read_timeout
        )
        try:
            client.initialize()
            return client.call_tool(tool_name, tool_args)
        except Exception as e:
            error_msg = f"Error executing tool: {str(e)}"
            logging.error(error_msg)
            return error_msg
        finally:
            client.close()