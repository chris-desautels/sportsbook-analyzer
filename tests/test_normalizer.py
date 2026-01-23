import pytest

from app.services.normalizer import (
    american_to_decimal,
    decimal_to_american,
    implied_prob_from_american,
    implied_prob_from_decimal,
    implied_prob_to_decimal,
)


def test_american_to_decimal():
    assert american_to_decimal(150) == 2.5
    assert round(american_to_decimal(-110), 2) == 1.91


def test_decimal_to_american():
    assert decimal_to_american(2.5) == 150
    assert decimal_to_american(1.91) == -110


def test_implied_probability_conversions():
    prob = implied_prob_from_american(150)
    assert round(prob, 3) == 0.4
    assert round(implied_prob_from_decimal(2.5), 3) == 0.4
    assert round(implied_prob_to_decimal(prob), 2) == 2.5


def test_invalid_inputs():
    with pytest.raises(ValueError):
        american_to_decimal(0)
    with pytest.raises(ValueError):
        decimal_to_american(1)
    with pytest.raises(ValueError):
        implied_prob_to_decimal(0)
