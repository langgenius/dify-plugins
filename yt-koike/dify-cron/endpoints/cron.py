import time
from typing import Mapping
import requests
from werkzeug import Request, Response
from dify_plugin import Endpoint
import datetime

started_api_keys = set()


class CronEndpoint(Endpoint):
    def is_now_to_call(self, cron_str):
        # Check if it is time to make a self call
        # This cron is mostly based on UNIX cron format: https://www.ibm.com/docs/en/db2-as-a-service?topic=task-unix-cron-format
        # Sunday = 0, Monday = 1, ... and lastly Saturday = 6
        # This cron also supports seconds.
        cron_str = cron_str.strip()
        if len(cron_str.split(" ")) != 6:
            raise Exception("Invalid cron setting")
        seconds, minutes, hours, days, months, weekdays = cron_str.split(" ")
        now = datetime.datetime.now()
        if seconds != "*":
            if not now.second in map(int, seconds.split(",")):
                return False
        if minutes != "*":
            if not now.minute in map(int, minutes.split(",")):
                return False
        if hours != "*":
            if not now.hour in map(int, hours.split(",")):
                return False
        if days != "*":
            if not now.day in map(int, days.split(",")):
                return False
        if months != "*":
            if not now.month in map(int, months.split(",")):
                return False
        if weekdays != "*":
            if not (now.weekday() + 1) % 7 in map(int, weekdays.split(",")):
                return False
        return True

    def _invoke(self, r: Request, values: Mapping, settings: Mapping) -> Response:
        """
        Invokes the endpoint with the given request.
        """
        command = values["command"]
        api_key = settings.get("api_key")
        endpoint_url = settings.get("endpoint_url").rstrip("/")
        cron_str = settings.get("cron_str")
        try:
            self.is_now_to_call(cron_str)
        except:
            raise Exception("Invalid cron setting")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "inputs": {},
            "query": "cron",
            "response_mode": "blocking",
            "conversation_id": "",
            "user": "cron",
            "files": [],
        }

        if len(command) == 0 or command == "status":
            return Response(
                (
                    "<html><head></head><body>Cron status: active <br><a href='./stop'>Stop?</a></body></html>"
                    if api_key in started_api_keys
                    else "<html><head></head><body>Cron status: inactive <br><a href='./start'>Start?</a></body></html>"
                ),
                status=200,
                content_type="text/html",
            )
        elif command == "stop":
            started_api_keys.remove(api_key)
            return Response(
                '<html><head></head><body>Stop requested. Returning in 5 seconds... <meta http-equiv="refresh" content="5;URL=./status"></body></html>',
                status=200,
                content_type="text/html",
            )
        elif command == "start":
            if api_key in started_api_keys:
                return Response(
                    '<html><head></head><body>Cron already started. Returning in 5 seconds... <meta http-equiv="refresh" content="5;URL=./status"></body></html>',
                    status=200,
                    content_type="text/html",
                )
            started_api_keys.add(api_key)
            while True:
                if not api_key in started_api_keys:
                    return Response("Cron Stopped")
                time.sleep(0.1)
                if self.is_now_to_call(cron_str):
                    requests.post(
                        endpoint_url + "/v1/chat-messages",
                        headers=headers,
                        json=data,
                    )
        else:
            return Response("Invalid Command")
