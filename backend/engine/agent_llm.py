"""LLM execution path for the agent core — a real Anthropic tool-calling loop.

Only imported when ANTHROPIC_API_KEY is set (see agent.run_agent). Tools mirror
the architecture: query_rag, check_suitability, build_comparison. The model must
finish by calling `emit_decision`, which yields the structured, bilingual nudge.

The LLM owns the *reasoning + copy + tool trace* (the visibly-agentic part); the
deterministic builders own the *grounded UI payload* via `agent.materialize_flow`,
so every flow (idle/FD/subscription/compare) renders identically to the rules
path. The whole thing is wrapped by `agent.run_agent`, which falls back to the
deterministic engine on any exception.
"""
from __future__ import annotations

import json
from typing import Any

import config
from engine import comparison, rag, suitability

_SYSTEM = """You are Saarthi, a trust-first, agentic adoption copilot inside a \
mocked SBI YONO banking app. You are given a user's detected "adoption moments" \
(found from their own transactions) and must decide whether to surface ONE nudge.

Non-negotiable rules:
- Never recommend a ULIP or any insurance-cum-investment product.
- State NO number that you did not retrieve via query_rag.
- Always run check_suitability before surfacing; if it blocks, suppress.
- For a premium-leak moment, call build_comparison so the user sees an honest,
  like-for-like comparison (including where the competitor wins).
- Prefer the single highest-value moment; suppress the rest with a reason.
- Write the nudge in BOTH English and natural Hindi. Keep it short and honest.
- It is valid to surface nothing.

Use the tools to gather grounding, then finish by calling emit_decision."""

_TOOLS = [
    {
        "name": "query_rag",
        "description": "Retrieve grounded snippets from the product corpus.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}, "k": {"type": "integer"}},
            "required": ["query"],
        },
    },
    {
        "name": "check_suitability",
        "description": "Run the hard suitability rules for a proposed product.",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_type": {"type": "string"},
                "monthly_cost": {"type": "number"},
            },
            "required": ["product_type"],
        },
    },
    {
        "name": "build_comparison",
        "description": "Build an honest term-insurance comparison vs a competitor.",
        "input_schema": {
            "type": "object",
            "properties": {"competitor": {"type": "string"}},
            "required": [],
        },
    },
    {
        "name": "emit_decision",
        "description": "Finish: emit the final decision and bilingual nudge.",
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["surface", "suppress", "stay_silent"]},
                "surfaced_trigger_type": {"type": "string"},
                "rationale": {"type": "string"},
                "title_en": {"type": "string"},
                "title_hi": {"type": "string"},
                "body_en": {"type": "string"},
                "body_hi": {"type": "string"},
                "cta_en": {"type": "string"},
                "cta_hi": {"type": "string"},
                "suppressed": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "trigger_type": {"type": "string"},
                            "reason": {"type": "string"},
                        },
                    },
                },
            },
            "required": ["action"],
        },
    },
]


def _run_tool(name: str, args: dict[str, Any], persona: dict[str, Any]) -> Any:
    if name == "query_rag":
        return rag.query_rag(args["query"], int(args.get("k", 3)))
    if name == "check_suitability":
        return suitability.check_suitability(
            product_type=args["product_type"],
            monthly_cost=float(args.get("monthly_cost", 0)),
            persona=persona,
        )
    if name == "build_comparison":
        return comparison.build_insurance_comparison(args.get("competitor"))
    return {"error": f"unknown tool {name}"}


def _finalize(
    d: dict[str, Any],
    moments: list[dict[str, Any]],
    persona: dict[str, Any],
    adopted_features: set[str],
    decision_log: list[dict[str, Any]],
) -> dict[str, Any]:
    """Turn the model's emit_decision into the same shape the deterministic path
    returns, materializing the flow-specific payload so the UI renders fully."""
    from engine import agent as _agent

    decision_log.append({"step": "act", "detail": d.get("rationale", "Decision emitted.")})
    nudge = {
        "title": {"en": d.get("title_en", ""), "hi": d.get("title_hi", "")},
        "body": {"en": d.get("body_en", ""), "hi": d.get("body_hi", "")},
        "cta": {"en": d.get("cta_en", ""), "hi": d.get("cta_hi", "")},
    }
    action = d.get("action", "surface")
    surfaced = next(
        (m for m in moments if m["trigger_type"] == d.get("surfaced_trigger_type")), None
    )
    result: dict[str, Any] = {
        "action": action,
        "surfaced_moment": surfaced,
        "nudge": nudge,
        "suppressed": d.get("suppressed", []),
        "decision_log": decision_log,
        "engine": "anthropic",
        "model": config.MODEL,
    }
    if action == "surface" and surfaced is not None:
        # Grounded UI payload (walkthrough / subscriptions / comparison / etc.)
        result.update(_agent.materialize_flow(persona, surfaced, adopted_features))
    return result


def run_agent_llm(
    persona: dict[str, Any],
    moments: list[dict[str, Any]],
    *,
    skipped_types: set[str] | None = None,
    adopted_features: set[str] | None = None,
    max_turns: int = 6,
) -> dict[str, Any]:
    from anthropic import Anthropic

    from engine import agent as _agent

    skipped_types = skipped_types or set()
    adopted_features = adopted_features or set()

    decision_log: list[dict[str, Any]] = [
        {"step": "perceive", "detail": f"{len(moments)} candidate moment(s) handed to the agent."}
    ]
    # Close the loop first — identical learn gate to the deterministic path.
    moments, learn = _agent.apply_learning(persona, moments, skipped_types, adopted_features)
    decision_log.extend(learn)
    if not moments:
        decision_log.append({"step": "act", "detail": "Nothing left worth surfacing — staying silent."})
        return {"action": "stay_silent", "decision_log": decision_log,
                "engine": "anthropic", "model": config.MODEL}

    client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
    user = {
        "persona": {k: persona.get(k) for k in ("persona_id", "name", "monthly_income")},
        "moments": moments,
    }
    messages: list[dict[str, Any]] = [
        {"role": "user", "content": "Decide on a nudge for:\n" + json.dumps(user, ensure_ascii=False)}
    ]

    for turn in range(max_turns):
        resp = client.messages.create(
            model=config.MODEL,
            max_tokens=config.MAX_TOKENS,
            system=_SYSTEM,
            tools=_TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": resp.content})

        tool_uses = [b for b in resp.content if getattr(b, "type", None) == "tool_use"]
        if not tool_uses:
            # The model replied with prose instead of finishing — nudge it once.
            if turn < max_turns - 1:
                messages.append({"role": "user", "content": "Please finish by calling emit_decision."})
                continue
            break

        results = []
        for tu in tool_uses:
            if tu.name == "emit_decision":
                return _finalize(tu.input, moments, persona, adopted_features, decision_log)
            out = _run_tool(tu.name, tu.input, persona)
            decision_log.append({"step": "reason", "tool": tu.name,
                                 "detail": json.dumps(tu.input, ensure_ascii=False),
                                 "result": out if not isinstance(out, list) else [r.get("id") for r in out]})
            results.append({"type": "tool_result", "tool_use_id": tu.id,
                            "content": json.dumps(out, ensure_ascii=False, default=str)})
        messages.append({"role": "user", "content": results})

    # Model never emitted a decision -> let the caller fall back.
    raise RuntimeError("LLM agent did not emit a decision within max_turns")
