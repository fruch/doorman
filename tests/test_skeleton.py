#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from doorman.skeleton import fib

__author__ = "Israel Fruchter (ifruchte)"
__copyright__ = "Israel Fruchter (ifruchte)"
__license__ = "simple-bsd"


def test_fib():
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13
    with pytest.raises(AssertionError):
        fib(-10)
