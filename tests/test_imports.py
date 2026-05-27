import importlib


def test_imports():
    modules = [
        "casper",
        "casper.core.runtime",
        "casper.evidence.registry",
        "casper.rules.engine",
        "casper.state.session",
        "casper.tools.init",
    ]

    for module in modules:
        importlib.import_module(module)
