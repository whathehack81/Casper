from gatekeeper import Gatekeeper
from casper.contracts.finding import Finding
from casper.contracts.rules import AdvancementRules


def test_gatekeeper_blocks_when_required_evidence_missing():
    finding = Finding(title="Candidate issue")
    rules = AdvancementRules(required_evidence=["request", "response"])

    evaluated = Gatekeeper(rules).evaluate(finding)

    assert evaluated.status == "blocked"
    assert evaluated.notes == ["missing:request,response"]


def test_gatekeeper_advances_when_required_evidence_present():
    finding = Finding(title="Candidate issue")
    finding.add_evidence("request", {"method": "GET", "url": "https://example.com"})
    finding.add_evidence("response", {"status": 200})

    rules = AdvancementRules(required_evidence=["request", "response"])

    evaluated = Gatekeeper(rules).evaluate(finding)

    assert evaluated.status == "ready"
    assert evaluated.notes == ["advance:requirements_satisfied"]


def test_advancement_rules_allows_only_when_requirements_met():
    finding = Finding(title="Candidate issue")
    finding.add_evidence("request", {"method": "GET"})

    rules = AdvancementRules(required_evidence=["request", "response"])

    assert rules.allows(finding) is False

    finding.add_evidence("response", {"status": 200})

    assert rules.allows(finding) is True
