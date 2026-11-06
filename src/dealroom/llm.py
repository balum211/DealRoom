"""Thin helpers around the chat model: one call, JSON parsing, and safe fallbacks."""
from __future__ import annotations

import json
import re
from typing import Any

from filingsight.llm import get_chat_model

_JSON_BLOCK = re.compile(r"(\{.*\}|\[.*\])", re.S)


def chat(system: str, user: str, temperature: float = 0.2) -> str:
    from langchain_core.messages import HumanMessage, SystemMessage

    model = get_chat_model(temperature=temperature)
    reply = model.invoke([SystemMessage(content=system), HumanMessage(content=user)])
    return str(reply.content)


def parse_json(text: str) -> Any:
    """Parse the first JSON object or array in a model reply (tolerates code fences and chatter)."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?|```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = _JSON_BLOCK.search(text)
        if not m:
            raise
        return json.loads(m.group(1))


def chat_json(system: str, user: str, temperature: float = 0.2) -> Any:
    return parse_json(chat(system, user, temperature))
