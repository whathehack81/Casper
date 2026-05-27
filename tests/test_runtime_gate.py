from casper.core.runtime import CasperRuntime
from casper.rules.engine import Rule


def test_runtime_gate_blocks_without_rules(tmp_path):
    runtime = CasperRuntime(tmp_path)

    assert runtime.validate() is False


def test_runtime_gate_allows_when_rules_pass(tmp_path):
    runtime = CasperRuntime(tmp_path)

    runtime.register_rule(
        Rule(
            name="evidence exists",
            check=lambda: True,
            pass_reason="ok",
            fail_reason="missing",
        )
    )

    assert runtime.validate() is True
