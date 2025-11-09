# test_calculator.py
import pytest
import calculator

def test_add():
    assert calculator.add(2, 3) == 5

def test_subtract():
    assert calculator.subtract(10, 4) == 6

def test_multiply():
    assert calculator.multiply(2, 5) == 10

def test_divide():
    assert calculator.divide(8, 2) == 4

def test_divide_by_zero():
    with pytest.raises(ValueError):
        calculator.divide(5, 0)
