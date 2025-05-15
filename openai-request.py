#!/usr/bin/env python3
"""
ask_llm.py – Query a STACKIT Model Serving chat model from the command line.

Usage:
    python ask_llm.py "What is STACKIT?"
    python ask_llm.py -m gpt-4o-mini -s "You are a helpful assistant." "How do I deploy a Django app on STACKIT?"

Environment variables (typically placed in a project‑root .env file):

    STACKIT_MODEL_SERVING_MODEL          # e.g. "gpt-4o-mini"
    STACKIT_MODEL_SERVING_BASE_URL       # e.g. "https://api.openai-compat.model-serving.eu01.onstackit.cloud/v1"
    STACKIT_MODEL_SERVING_AUTH_TOKEN     # Bearer token like "ey..."

Dependencies:
    pip install openai python-dotenv
"""

import argparse
import os
import sys
from dotenv import load_dotenv

# OpenAI SDK v1.0+ preferred, but we'll seamlessly support older 0.X versions too.
try:
    from openai import OpenAI  # noqa: E402
    _OPENAI_V1 = True
except ImportError:  # pragma: no cover – v1 not installed
    import openai  # type: ignore  # noqa: E402
    _OPENAI_V1 = False


def main() -> None:  # pragma: no cover
    parser = argparse.ArgumentParser(
        prog="ask_llm.py",
        description="Send a chat completion request to STACKIT Model Serving.",
    )
    parser.add_argument(
        "question",
        help="Your user prompt / question to the assistant.",
    )
    parser.add_argument(
        "-m",
        "--model",
        help="Override the model ID from environment variable.",
        default=None,
    )
    parser.add_argument(
        "-s",
        "--system",
        help="Optional system prompt.",
        default="You are a helpful assistant.",
    )
    parser.add_argument(
        "-e",
        "--env",
        help="Path to .env file (default: ../.env)",
        default=".env",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Sampling temperature (0 = deterministic, 1 = very creative).",
    )
    args = parser.parse_args()

    # Load environment variables early so CLI overrides can use them.
    load_dotenv(args.env)

    model = args.model or os.getenv("STACKIT_MODEL_SERVING_MODEL")
    base_url = os.getenv("STACKIT_MODEL_SERVING_BASE_URL")
    token = os.getenv("STACKIT_MODEL_SERVING_AUTH_TOKEN")

    missing = [name for name, val in (
        ("STACKIT_MODEL_SERVING_MODEL", model),
        ("STACKIT_MODEL_SERVING_BASE_URL", base_url),
        ("STACKIT_MODEL_SERVING_AUTH_TOKEN", token),
    ) if not val]
    if missing:
        sys.exit(
            f"❌ Missing required env vars: {', '.join(missing)}\n"
            "Create or update your .env file or export them in the shell."
        )

    # --- Call the model -----------------------------------------------------
    try:
        if _OPENAI_V1:
            client = OpenAI(api_key=token, base_url=base_url)
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": args.system},
                    {"role": "user", "content": args.question.strip()},
                ],
                temperature=args.temperature,
            )
            print(response.choices[0].message.content.strip())
        else:  # openai < 1.0 fallback
            openai.api_key = token  # type: ignore[misc]
            # Some 0.X versions expect api_base instead of base_url
            if hasattr(openai, "api_base"):
                openai.api_base = base_url  # type: ignore[attr-defined]
            else:
                openai.base_url = base_url  # type: ignore[attr-defined]

            response = openai.ChatCompletion.create(  # type: ignore[attr-defined]
                model=model,
                messages=[
                    {"role": "system", "content": args.system},
                    {"role": "user", "content": args.question.strip()},
                ],
                temperature=args.temperature,
            )
            print(response["choices"][0]["message"]["content"].strip())
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    except Exception as exc:  # pragma: no cover
        sys.exit(f"❌ Request failed: {exc}")


if __name__ == "__main__":
    main()
