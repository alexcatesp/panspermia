import pytest

from panspermia.island import setup_determinism

setup_determinism()


def pytest_addoption(parser):
    parser.addoption("--runslow", action="store_true", default=False, help="ejecuta tests lentos")


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: test largo (minutos); requiere --runslow")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        return
    skip = pytest.mark.skip(reason="lento: usar --runslow")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip)
