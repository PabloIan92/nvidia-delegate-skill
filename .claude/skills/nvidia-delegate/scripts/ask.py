#!/usr/bin/env python3
"""Send a bounded text-only task to an NVIDIA NIM model."""

import argparse
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request


DEFAULT_BASE_URL = "https://integrate.api.nvidia.com/v1"


def load_api_key():
    api_key = os.environ.get("NVIDIA_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("NVIDIA_API_KEY is not set")
    return api_key


def compact_output(text, max_lines=12, max_words=250):
    if max_lines < 1 or max_words < 1:
        raise ValueError("output limits must be positive")

    source_lines = text.strip().splitlines()
    result = []
    remaining_words = max_words
    truncated = False

    for line in source_lines:
        if len(result) >= max_lines:
            truncated = True
            break

        words = line.split()
        if len(words) <= remaining_words:
            result.append(line.rstrip())
            remaining_words -= len(words)
            continue

        if remaining_words:
            result.append(" ".join(words[:remaining_words]))
        truncated = True
        break

    if len(source_lines) > len(result) and remaining_words == 0:
        truncated = True

    if truncated:
        if not result:
            result.append("[truncated]")
        elif len(result) < max_lines:
            result.append("[truncated]")
        else:
            result[-1] = f"{result[-1]} [truncated]"

    return "\n".join(result)


def read_prompt(prompt, file_path):
    if prompt is not None and file_path is not None:
        raise ValueError("use either a prompt argument or --file, not both")
    if file_path is not None:
        return Path(file_path).read_text(encoding="utf-8")
    if prompt in (None, "-"):
        return sys.stdin.read()
    return prompt


def request_completion(model, prompt, api_key, base_url, max_tokens):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": max_tokens,
        "stream": False,
    }
    if model.startswith("deepseek-ai/"):
        payload["chat_template_kwargs"] = {"thinking": False}

    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        data = json.loads(response.read().decode("utf-8"))

    message = data["choices"][0]["message"]
    content = message.get("content") or message.get("reasoning_content")
    if not content:
        raise RuntimeError("NVIDIA returned an empty response")
    return content


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", help="NVIDIA API model ID")
    parser.add_argument("prompt", nargs="?", help="prompt text, or - for stdin")
    parser.add_argument("--file", help="read the prompt from this UTF-8 file")
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--max-lines", type=int, default=12)
    parser.add_argument("--max-words", type=int, default=250)
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        if args.max_tokens < 1:
            raise ValueError("--max-tokens must be positive")
        prompt = read_prompt(args.prompt, args.file)
        if not prompt.strip():
            raise ValueError("prompt is empty")
        content = request_completion(
            model=args.model,
            prompt=prompt,
            api_key=load_api_key(),
            base_url=os.environ.get("NVIDIA_BASE_URL", DEFAULT_BASE_URL),
            max_tokens=args.max_tokens,
        )
        print(compact_output(content, args.max_lines, args.max_words))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")[:1000]
        print(f"HTTP {error.code}: {body}", file=sys.stderr)
        return 1
    except (OSError, KeyError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
