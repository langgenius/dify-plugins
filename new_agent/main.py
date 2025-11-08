import argparse
import os
import sys
from typing import Optional

# Optional dependency: dotenv
try:
    from dotenv import load_dotenv  # type: ignore
except Exception:  # pragma: no cover
    def load_dotenv(override: bool = False) -> None:  # type: ignore
        return None

# Optional dependency: rich
try:
    from rich.console import Console  # type: ignore
    from rich.prompt import Prompt  # type: ignore
except Exception:  # pragma: no cover
    Console = None  # type: ignore
    Prompt = None  # type: ignore

try:
    # The OpenAI SDK is optional for offline mode
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore

console = Console() if Console else None


def load_environment() -> None:
    """Load environment variables from a local .env file if present."""
    try:
        load_dotenv(override=False)
    except Exception:
        # If python-dotenv is not installed, skip silently
        pass


def ensure_openai_client_or_exit() -> "OpenAI":
    """Create the OpenAI client or exit with a helpful message if unavailable."""
    if OpenAI is None:
        if console:
            console.print("[bold red]openai[/bold red] package not installed. Run inside venv: \n  pip install -r requirements.txt")
        else:
            print("openai package not installed. Run: pip install -r requirements.txt")
        sys.exit(2)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        message = (
            "OPENAI_API_KEY is not set. Add it to your environment or a .env file.\n"
            "Example: echo 'OPENAI_API_KEY=sk-...' > .env"
        )
        if console:
            console.print(f"[yellow]{message}[/yellow]")
        else:
            print(message)
        # We still return a client; the SDK will error on use, but this message is clearer.
    return OpenAI()


def request_completion(
    client: "OpenAI",
    user_message: str,
    model: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.2,
    max_tokens: Optional[int] = None,
) -> str:
    """Request a chat completion from OpenAI and return content text."""
    resolved_system_prompt = system_prompt or (
        "You are a helpful, concise assistant. Reply in the user's language."
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": resolved_system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    choice = response.choices[0]
    return choice.message.content or ""


def run_single_turn(
    offline: bool,
    query: str,
    model: str,
    temperature: float,
    max_tokens: Optional[int],
) -> int:
    """Execute a single-turn request and print the answer."""
    if offline:
        if console:
            console.print("[green]Offline mode:[/green] agent initialized; skipping API call.")
            console.print(f"Q: {query}")
            console.print("A: (offline) 这是一个占位响应，用于验证智能体已成功启动。")
        else:
            print("Offline mode: agent initialized; skipping API call.")
            print(f"Q: {query}")
            print("A: (offline) 这是一个占位响应，用于验证智能体已成功启动。")
        return 0

    client = ensure_openai_client_or_exit()
    try:
        answer = request_completion(
            client=client,
            user_message=query,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    except Exception as exc:  # Surface clear error to user
        if console:
            console.print(f"[red]Request failed:[/red] {exc}")
        else:
            print(f"Request failed: {exc}")
        return 2

    if console:
        console.print(answer)
    else:
        print(answer)
    return 0


def run_interactive_loop(model: str) -> int:
    """Start a simple REPL chat loop until the user types 'exit'."""
    client = ensure_openai_client_or_exit()
    if console:
        console.print("[bold]Interactive chat[/bold]. Type 'exit' to quit.")
    else:
        print("Interactive chat. Type 'exit' to quit.")

    while True:
        if Prompt and console:
            user_text = Prompt.ask("You")
        else:
            user_text = input("You: ")
        if user_text.strip().lower() in {"exit", "quit", ":q"}:
            if console:
                console.print("Bye!")
            else:
                print("Bye!")
            return 0
        try:
            answer = request_completion(client=client, user_message=user_text, model=model)
        except Exception as exc:
            if console:
                console.print(f"[red]Request failed:[/red] {exc}")
            else:
                print(f"Request failed: {exc}")
            return 2
        if console:
            console.print(f"[cyan]Agent[/cyan]: {answer}")
        else:
            print(f"Agent: {answer}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Minimal CLI agent")
    parser.add_argument("--ask", "-q", type=str, help="Ask a single question and exit")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="Model name")
    parser.add_argument("--temperature", type=float, default=0.2, help="Sampling temperature")
    parser.add_argument("--max-tokens", type=int, default=None, help="Max tokens for the response")
    parser.add_argument("--offline", action="store_true", help="Skip API calls and print a placeholder answer")
    return parser


if __name__ == "__main__":
    load_environment()
    args = build_arg_parser().parse_args()

    if args.ask:
        sys.exit(
            run_single_turn(
                offline=args.offline,
                query=args.ask,
                model=args.model,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
            )
        )

    if args.offline:
        if console:
            console.print("[green]Offline mode:[/green] agent initialized; interactive mode is not available offline.")
        else:
            print("Offline mode: agent initialized; interactive mode is not available offline.")
        sys.exit(0)

    sys.exit(run_interactive_loop(model=args.model))
