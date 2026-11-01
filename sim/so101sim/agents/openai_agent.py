"""LLM-as-policy agent using the OpenAI Responses API (default model: gpt-6-astra).

Loop: send instruction + initial images -> model calls tools -> we execute them
on the robot and return results + fresh camera images -> repeat until
`finish`, a turn/time budget, or the model stops calling tools.

Two context modes:
  server  - use previous_response_id; the server keeps the full history
            (simplest; cost grows with every image ever sent).
  window  - we keep the history locally and replace images older than the
            last N observations with a text placeholder (cheaper; research knob).
"""
from __future__ import annotations

import base64
import io
import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image

from ..tools import FRAME_DOC, tool_schemas

PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "system.md"


def _b64_image(img, fmt="JPEG", quality=85) -> str:
    buf = io.BytesIO()
    Image.fromarray(img).save(buf, format=fmt, quality=quality)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


@dataclass
class Pricing:
    """USD per 1M tokens. Defaults are third-party figures for gpt-6-astra (unverified) - override via CLI."""
    input: float = 10.0
    cached_input: float = 1.0
    output: float = 50.0


@dataclass
class Usage:
    calls: int = 0
    input_tokens: int = 0
    cached_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0
    latency_s: float = 0.0
    per_call: list = field(default_factory=list)

    def add(self, u, dt):
        self.calls += 1
        self.latency_s += dt
        if u is None:
            return
        it = getattr(u, "input_tokens", 0) or 0
        ot = getattr(u, "output_tokens", 0) or 0
        ct = getattr(getattr(u, "input_tokens_details", None), "cached_tokens", 0) or 0
        rt = getattr(getattr(u, "output_tokens_details", None), "reasoning_tokens", 0) or 0
        self.input_tokens += it; self.output_tokens += ot; self.cached_tokens += ct; self.reasoning_tokens += rt
        self.per_call.append({"in": it, "cached": ct, "out": ot, "reasoning": rt, "latency_s": round(dt, 2)})

    def cost(self, p: Pricing) -> float:
        fresh = self.input_tokens - self.cached_tokens
        return (fresh * p.input + self.cached_tokens * p.cached_input + self.output_tokens * p.output) / 1e6


class OpenAIAgent:
    name = "openai"

    def __init__(self, model="gpt-6-astra", effort="medium", logger=None, max_turns=60, max_wall_s=3600,
                 context_mode="server", image_window=2, image_detail="high", pricing: Pricing | None = None,
                 client=None, system_prompt: str | None = None):
        self.model, self.effort = model, effort
        self.log = logger
        self.max_turns, self.max_wall_s = max_turns, max_wall_s
        self.context_mode, self.image_window = context_mode, image_window
        self.image_detail = image_detail
        self.pricing = pricing or Pricing()
        self.usage = Usage()
        if client is None:
            from openai import OpenAI  # reads OPENAI_API_KEY / OPENAI_BASE_URL
            client = OpenAI()
        self.client = client
        text = system_prompt or PROMPT_PATH.read_text()
        self.instructions = text.replace("{FRAME_DOC}", FRAME_DOC)
        self.stop_reason = None

    # ---------------------------------------------------------- messages
    def _obs_message(self, header: str, images: dict) -> dict:
        content = [{"type": "input_text", "text": header}]
        for cam, img in images.items():
            content.append({"type": "input_text", "text": f"[{cam} camera]"})
            content.append({"type": "input_image", "image_url": _b64_image(img), "detail": self.image_detail})
        return {"role": "user", "content": content}

    def _prune_images(self, history: list):
        """window mode: keep images only in the last N observation messages."""
        obs_idx = [i for i, m in enumerate(history)
                   if isinstance(m, dict) and m.get("role") == "user"
                   and any(c.get("type") == "input_image" for c in m["content"])]
        for i in obs_idx[:-self.image_window] if self.image_window > 0 else obs_idx:
            history[i] = {"role": "user", "content": [
                c if c.get("type") != "input_image" else {"type": "input_text", "text": "(older image omitted)"}
                for c in history[i]["content"]]}

    def _create(self, input_items, previous_id):
        kw = dict(model=self.model, instructions=self.instructions, input=input_items,
                  tools=tool_schemas(), parallel_tool_calls=False)
        if self.effort:
            kw["reasoning"] = {"effort": self.effort}
        if previous_id:
            kw["previous_response_id"] = previous_id
        t = time.time()
        resp = self.client.responses.create(**kw)
        self.usage.add(getattr(resp, "usage", None), time.time() - t)
        return resp

    # --------------------------------------------------------------- run
    def run(self, tools, instruction: str, sim=None):
        t_start = time.time()
        first = self._obs_message(
            f"TASK: {instruction}\n\nCurrent robot state:\n{json.dumps(tools.state())}\n\nInitial camera images follow.",
            tools.images())
        if self.log:
            self.log.event("instruction", text=instruction)
            self.log.note(f"## Task\n{instruction}")
        history = [first]
        pending = [first]
        previous_id = None
        idle_turns = 0

        for turn in range(self.max_turns):
            if time.time() - t_start > self.max_wall_s:
                self.stop_reason = "wall-time budget exhausted"
                break
            if self.context_mode == "server":
                resp = self._create(pending, previous_id)
                previous_id = resp.id
            else:
                self._prune_images(history)
                resp = self._create(history, None)
                history.extend(_dump(o) for o in resp.output)

            calls = [o for o in resp.output if getattr(o, "type", None) == "function_call"]
            text = getattr(resp, "output_text", "") or ""
            if self.log:
                self.log.model_text(text)
                self.log.event("usage", turn=turn, **(self.usage.per_call[-1] if self.usage.per_call else {}))

            if not calls:
                idle_turns += 1
                if idle_turns >= 2:
                    self.stop_reason = "model stopped calling tools"
                    break
                nudge = {"role": "user", "content": [{"type": "input_text", "text":
                         "Continue by calling a tool. Call finish(success, summary) when the task is complete."}]}
                pending = [nudge]; history.append(nudge)
                continue
            idle_turns = 0

            outputs, all_images, headers = [], {}, []
            for c in calls:
                try:
                    args = json.loads(c.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                result, images = tools.call(c.name, args)
                if self.log:
                    self.log.tool_call(c.name, args, result, images)
                outputs.append({"type": "function_call_output", "call_id": c.call_id,
                                "output": json.dumps(result, ensure_ascii=False)})
                if images:
                    all_images = images  # keep only the latest observation set
                    headers.append(c.name)
            if tools.finished is not None:
                self.stop_reason = "finish called"
                break
            pending = list(outputs)
            if all_images:
                pending.append(self._obs_message(f"Camera images after: {', '.join(headers)}", all_images))
            history.extend(pending)
        else:
            self.stop_reason = "turn budget exhausted"

        return {
            "stop_reason": self.stop_reason,
            "llm_calls": self.usage.calls,
            "input_tokens": self.usage.input_tokens,
            "cached_tokens": self.usage.cached_tokens,
            "output_tokens": self.usage.output_tokens,
            "reasoning_tokens": self.usage.reasoning_tokens,
            "llm_latency_s": round(self.usage.latency_s, 1),
            "est_cost_usd": round(self.usage.cost(self.pricing), 4),
        }


def _dump(item):
    """Convert an SDK output item back into an input item (window mode)."""
    if getattr(item, "type", None) == "function_call":
        return {"type": "function_call", "call_id": item.call_id, "name": item.name, "arguments": item.arguments}
    if hasattr(item, "model_dump"):
        return item.model_dump(exclude_none=True)
    return dict(vars(item))
