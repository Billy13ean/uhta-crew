"""Diagnostic probe for the mechanic-designer refusal.

Place at crew/probe_refusal.py (crew/ is COPYed into the image), then:

    docker compose build
    docker compose run --rm --entrypoint python3 crew crew/probe_refusal.py

Isolates whether stop_reason='refusal' comes from the system prompt, the
packet's contents, or the packet's size. Each line prints the stop_reason the
API actually returned, so the first line that reads 'refusal' names the cause.

Every call caps max_tokens at 1024 -- this is a probe, not a generation run.
"""
from __future__ import annotations

import glob
import os
import sys

import anthropic

MODEL = os.environ.get("CREW_MODEL") or "claude-sonnet-4-5"
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"].strip())


def call(label: str, system: str, user: str, max_tokens: int = 1024) -> None:
    try:
        with client.messages.stream(
            model=MODEL,
            max_tokens=max_tokens,
            temperature=0.2,
            system=system,
            messages=[{"role": "user", "content": user}],
        ) as stream:
            msg = stream.get_final_message()
        text = "".join(
            b.text for b in msg.content if getattr(b, "type", "") == "text"
        )
        blocks = [getattr(b, "type", "?") for b in msg.content]
        print(
            f"[{label:<32}] stop_reason={str(msg.stop_reason):<12} "
            f"blocks={blocks} chars={len(text)}"
        )
    except Exception as exc:  # noqa: BLE001 -- a probe reports, it does not raise
        print(f"[{label:<32}] EXCEPTION {type(exc).__name__}: {exc}")


packets = sorted(glob.glob("out/*/packet-mechanic-designer-*.md"), key=__import__("os").path.getmtime)   # newest by TIME — alphabetical picked a stale run
if not packets:
    sys.exit("No packet found under out/. Run the crew once first.")

packet_path = packets[-1]
packet = open(packet_path, encoding="utf-8").read()

prompt = open("prompts/mechanic-designer.md", encoding="utf-8").read()
_, _, body = prompt.partition("## SYSTEM")
system, marker, rest = body.partition("## CONTEXT PACKET")
system = system.strip()

print(f"model:  {MODEL}")
print(f"packet: {packet_path} ({len(packet)} chars)")
print(f"system: {len(system)} chars")
print()

# 1. Is the key/model/transport working at all?
call("control: trivial", "You are helpful.", "Say OK.")

# 2. Does the real system prompt alone trip it?
call("real system, trivial user", system, "Reply with the single word READY.")

# 3. Does the packet trip it even with a bland system prompt?
call(
    "bland system, full packet",
    "You are a helpful assistant.",
    packet + "\n\nReply with the single word READY.",
)

# 4. Size ladder -- where does it flip?
for n in (2000, 4000, 8000, 16000):
    call(
        f"real system + packet[:{n}]",
        system,
        packet[:n] + "\n\nReply with the single word READY.",
    )

print()
print("Reading it:")
print("  control refuses          -> account/model level, not your content")
print("  system-only refuses      -> the system prompt text is the trigger")
print("  bland+packet refuses     -> the packet's CONTENT is the trigger")
print("  only the large ones fail -> a specific later section is the trigger;")
print("                              bisect between the last OK size and the first refusal")
