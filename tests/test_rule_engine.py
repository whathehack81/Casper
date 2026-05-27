from casper.rules.engine import Rule, RuleEngine


def test_rule_engine_blocks_without_rules():
    engine = RuleEngine()

    assert engine.can_advance() is False


def test_rule_engine_passes_when_all_rules_pass():
    engine = RuleEngine()
    engine.register(
        Rule(
            name="has evidence",
            check=lambda: True,
            pass_reason="evidence present",
            fail_reason="missing evidence",
        )
    )

    results = engine.evaluate()

    assert results[0].passed is True
    assert engine.can_advance() is True


def test_rule_engine_blocks_when_rule_fails():
    engine = RuleEngine()
    engine.register(
        Rule(
            name="has impact",
            check=lambda: False,
            pass_reason="impact proven",
            fail_reason="impact missing",
        )
    )

    results = engine.evaluate()

    assert results[0].passed is False
    assert results[0].reason == "impact missing"
    assert engine.can_advance() is False
