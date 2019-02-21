import os

import pytest


@pytest.fixture(autouse=True)
def enable_database(db):
    pass


@pytest.fixture
def rootdir():
    return os.path.dirname(os.path.abspath(__file__))
