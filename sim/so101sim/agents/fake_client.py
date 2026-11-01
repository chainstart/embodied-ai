"""Offline stand-in for `openai.OpenAI()` used by --agent dry-run.

Mimics the Responses API surface the agent uses (responses.create -> object with
.id, .output[*].type/.name/.arguments/.call_id, .output_text, .usage) and checks
that the request payload is well-formed. No network, no API key.
"""
from __future__ import annotations

import itertools
import json
from types import SimpleNamespace as NS

SCRIPT = [
    ("get_observation", {"cameras": ["top"]}),
    ("pixel_to_world", {"camera": "top", "u": 320, "v": 240}),
    ("set_gripper", {"opening": 1.0}),
    ("move_to", {"x": 0.22, "y": 0.0, "z": 0.08, "pitch_deg": -90}),
    ("move_relative", {"dz": 0.03}),
    ("go_home", {}),
    ("finish", {"success": False, "summary": "dry run"}),
]


class _Responses:
    def __init__(self):
        self.i = 0
        self.ids = itertools.count()
        self.requests = []

    def create(self, **kw):
        self.requests.append(kw)
        assert kw["model"] and isinstance(kw["input"], list) and kw["tools"], "malformed request"
        for item in kw["input"]:
            assert isinstance(item, dict), f"input item must be dict, got {type(item)}"
            if item.get("type") == "function_call_output":
                assert item["call_id"] and isinstance(item["output"], str)
            elif item.get("role") == "user":
                for c in item["content"]:
                    assert c["type"] in ("input_text", "input_image")
                    if c["type"] == "input_image":
                        assert c["image_url"].startswith("data:image/")
        name, args = SCRIPT[min(self.i, len(SCRIPT) - 1)]
        self.i += 1
        n = next(self.ids)
        usage = NS(input_tokens=5000, output_tokens=300,
                   input_tokens_details=NS(cached_tokens=2000), output_tokens_details=NS(reasoning_tokens=200))
        call = NS(type="function_call", name=name, arguments=json.dumps(args), call_id=f"call_{n}", id=f"fc_{n}")
        return NS(id=f"resp_{n}", output=[call], output_text=f"(dry-run step {n}: {name})", usage=usage)


class FakeOpenAI:
    def __init__(self):
        self.responses = _Responses()
