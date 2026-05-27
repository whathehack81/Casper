"""
Casper rule engine.

Rules decide whether execution can advance.
No rule pass means no advancement.
"""

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class RuleResult:
    name: str
    passed: bool
    reason: str


@dataclass(frozen=True)
class Rule:
    name: str
    check: Callable[[], bool]
    pass_reason: str
    fail_reason: str


class RuleEngine:
    def __init__(self) -> None:
        self.rules: list[Rule] = []
        self.results: list[RuleResult] = []

    def register(self, rule: Rule) -> None:
        self.rules.append(rule)
        self.results = []

    def evaluate(self) -> list[RuleResult]:
        results: list[RuleResult] = []

        for rule in self.rules:
            passed = rule.check()
            results.append(
                RuleResult(
                    name=rule.name,
                    passed=passed,
                    reason=rule.pass_reason if passed else rule.fail_reason,
                )
            )

        self.results = results
        return list(self.results)

    def can_advance(self) -> bool:
        if not self.rules:
            return False

        results = self.results or self.evaluate()
        return all(result.passed for result in results)
