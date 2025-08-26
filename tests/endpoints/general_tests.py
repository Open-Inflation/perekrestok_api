# general_tests.py
from __future__ import annotations

import pytest
from conftest import make_test

# Все независимые кейсы — в матрицу
@pytest.mark.parametrize(
    "factory",
    [
        lambda api: api.General.cities,
        lambda api: api.General.application_settings,
        lambda api: api.General.statuses,
    ],
    ids=["cities", "application_settings", "statuses"],
)
def test_general_matrix(api, schemashot, factory):
    make_test(schemashot, factory(api))
