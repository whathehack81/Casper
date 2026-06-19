from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from casper.contracts.finding import Finding
from casper.contracts.rules import AdvancementRules
from gatekeeper import Gatekeeper


@dataclass(frozen=True)
class ValidationProfile:
    mode: str
    name: str
    required_evidence: list[str]
    required_proof: list[str]
    min_confidence: float
    require_confirmation: bool = True
    min_linked_evidence: int = 1


@dataclass(frozen=True)
class ReasoningDecision:
    finding_id: str | None
    title: str
    mode: str
    profile: str
    validation_state: str
    confirmation_status: str
    confidence: float
    matched_evidence_ids: list[str]
    missing_evidence: list[str]
    proof_requirements: list[str]
    reasons: list[str]
    false_positive_reason: str | None
    can_advance: bool


PROFILES: dict[str, ValidationProfile] = {
    "web": ValidationProfile(
        mode="web",
        name="web-live-strict",
        required_evidence=["http"],
        required_proof=["request", "response", "observation"],
        min_confidence=0.65,
    ),
    "api": ValidationProfile(
        mode="api",
        name="api-live-strict",
        required_evidence=["http", "metadata"],
        required_proof=["request", "response", "status", "observation"],
        min_confidence=0.70,
    ),
    "mobile": ValidationProfile(
        mode="mobile",
        name="mobile-assessment-strict",
        required_evidence=["manual", "metadata"],
        required_proof=["target", "observation"],
        min_confidence=0.60,
        require_confirmation=False,
        min_linked_evidence=2,
    ),
    "code": ValidationProfile(
        mode="code",
        name="code-review-strict",
        required_evidence=["code", "patch", "metadata"],
        required_proof=["reference", "code-context", "observation"],
        min_confidence=0.75,
        min_linked_evidence=3,
    ),
    "blockchain": ValidationProfile(
        mode="blockchain",
        name="blockchain-review-strict",
        required_evidence=["code", "patch", "metadata"],
        required_proof=["reference", "code-context", "observation"],
        min_confidence=0.80,
        min_linked_evidence=3,
    ),
}


def get_profile(mode: str | None) -> ValidationProfile:
    selected = mode or "web"
    return PROFILES.get(selected, PROFILES["web"])


def _entry_kinds(entry: Any) -> set[str]:
    content = getattr(entry, "content", {})
    source = str(getattr(entry, "source", "")).lower()
    evidence_type = str(content.get("evidence_type", "")).lower()
    kinds: set[str] = set()

    if evidence_type:
        kinds.add(evidence_type)

    if source == "http-probe":
        kinds.update({"http", "metadata"})
    if source == "manual-check":
        kinds.add("manual")
        if "status" in content:
            kinds.add("http")
    if "patch" in source or "diff" in source or evidence_type == "patch":
        kinds.update({"patch", "code"})
    if "grep" in source or "source" in source or evidence_type == "code":
        kinds.add("code")
    if "repo" in source or "meta" in source or evidence_type == "metadata":
        kinds.add("metadata")

    if "command" in content or source.startswith("tool-") or source == "command-exec":
        kinds.add("command")

    return kinds


def _proof_tokens(entry: Any) -> set[str]:
    content = getattr(entry, "content", {})
    source = str(getattr(entry, "source", "")).lower()
    proof = {
        f"proof:{item}"
        for item in content.get("proof", [])
        if isinstance(item, str) and item
    }

    if content.get("target") or content.get("url"):
        proof.update({"proof:request", "proof:target"})
    if "status" in content or "ok" in content or content.get("content_type"):
        proof.update({"proof:response", "proof:status"})
    if content.get("observation"):
        proof.add("proof:observation")
    if content.get("command") or content.get("sha256"):
        proof.add("proof:artifact")
    if "repo" in source or "meta" in source:
        proof.add("proof:reference")
    if (
        "grep" in source
        or "source" in source
        or "patch" in source
        or "diff" in source
        or content.get("evidence_type") in {"code", "patch"}
    ):
        proof.add("proof:code-context")

    return proof


def _supportive_entries(entries: list[Any]) -> list[Any]:
    supported = []
    for entry in entries:
        content = getattr(entry, "content", {})
        result = content.get("result")
        status = content.get("status")
        ok = content.get("ok")
        if result in {"observed", "confirmed"}:
            supported.append(entry)
            continue
        if ok is True:
            supported.append(entry)
            continue
        if isinstance(status, int) and 200 <= status < 400:
            supported.append(entry)
    return supported


def _contradicted(entries: list[Any]) -> bool:
    if not entries:
        return False

    results = {getattr(entry, "content", {}).get("result") for entry in entries}
    return results <= {"blocked", "failed"}


def analyze_finding(
    finding: Finding,
    linked_entries: list[Any],
    mode: str | None,
) -> ReasoningDecision:
    profile = get_profile(mode)
    kinds = set()
    proof_tokens = set()
    evidence_items: list[dict[str, str]] = []
    reasons: list[str] = []

    for entry in linked_entries:
        entry_kinds = _entry_kinds(entry)
        kinds.update(entry_kinds)
        proof_tokens.update(_proof_tokens(entry))

    for kind in sorted(kinds):
        evidence_items.append({"kind": kind, "value": kind})
    for token in sorted(proof_tokens):
        evidence_items.append({"kind": token, "value": token})

    linked_count = len(linked_entries)
    supportive = _supportive_entries(linked_entries)
    supportive_ids = [entry.evidence_id for entry in supportive]

    base_missing = [
        required
        for required in profile.required_evidence
        if required not in kinds
    ]
    proof_requirements = [f"proof:{item}" for item in profile.required_proof]
    proof_missing = [
        required
        for required in proof_requirements
        if required not in proof_tokens
    ]

    if linked_count < profile.min_linked_evidence:
        base_missing.append(f"linked_evidence>={profile.min_linked_evidence}")

    coverage_total = len(profile.required_evidence) + len(proof_requirements) + 1
    matched = (
        len(profile.required_evidence) - len([item for item in base_missing if not item.startswith("linked_evidence>=")])
        + len(proof_requirements) - len(proof_missing)
        + min(linked_count, profile.min_linked_evidence) / max(profile.min_linked_evidence, 1)
    )
    confidence = round(min(1.0, matched / coverage_total), 2)

    manual_false_positive_reason = finding.false_positive_reason
    contradicted = _contradicted(linked_entries) and not supportive
    if manual_false_positive_reason:
        validation_state = "false_positive"
        confirmation_status = "rejected"
        reasons.append(f"finding marked false positive: {manual_false_positive_reason}")
    elif contradicted:
        validation_state = "false_positive"
        confirmation_status = "rejected"
        manual_false_positive_reason = "supporting evidence contradicted the claim"
        reasons.append(manual_false_positive_reason)
    elif not base_missing and not proof_missing:
        validation_state = "confirmed"
        confirmation_status = "confirmed"
        reasons.append("profile evidence and proof requirements satisfied")
    elif not base_missing:
        validation_state = "supported"
        confirmation_status = "needs-proof"
        reasons.append("supporting evidence exists but proof is incomplete")
    else:
        validation_state = "incomplete"
        confirmation_status = "unconfirmed"
        reasons.append("required evidence is still missing")

    finding.confidence = confidence
    finding.proof_requirements = list(proof_requirements)
    finding.validation_state = validation_state
    finding.confirmation_status = confirmation_status
    finding.false_positive_reason = manual_false_positive_reason

    rules = AdvancementRules(
        required_evidence=[
            *profile.required_evidence,
            *proof_requirements,
        ],
        min_confidence=profile.min_confidence,
        require_confirmation=profile.require_confirmation,
        metadata={
            "mode": profile.mode,
            "profile": profile.name,
        },
    )
    evaluated = Gatekeeper(rules).evaluate(
        finding,
        evidence_items=evidence_items,
    )

    if evaluated.status == "ready":
        reasons.append("gatekeeper marked finding ready for advancement")
    else:
        reasons.append("gatekeeper blocked advancement")

    finding.reasoning = list(dict.fromkeys(reasons))

    return ReasoningDecision(
        finding_id=finding.finding_id,
        title=finding.title,
        mode=profile.mode,
        profile=profile.name,
        validation_state=finding.validation_state,
        confirmation_status=finding.confirmation_status,
        confidence=finding.confidence,
        matched_evidence_ids=supportive_ids,
        missing_evidence=list(finding.missing_evidence),
        proof_requirements=list(finding.proof_requirements),
        reasons=list(finding.reasoning),
        false_positive_reason=finding.false_positive_reason,
        can_advance=evaluated.status == "ready",
    )
