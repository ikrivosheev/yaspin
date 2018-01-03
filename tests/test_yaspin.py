# -*- coding: utf-8 -*-

"""
tests.test_yaspin
~~~~~~~~~~~~~~~~~

Basic unittests.
"""

from __future__ import absolute_import

from collections import namedtuple
from inspect import getsource

import pytest

from yaspin import Spinner, yaspin
from yaspin.base_spinner import default_spinner
from yaspin.compat import builtin_str, str
from yaspin.termcolor import colored


ids = [
    "default frames and interval",
    "str text, str frames",
    "unicode text, unicode frames (marked as unicode)",
    "unicode text, str frames",
    "str text, unicode frames",
    "str text, List[] frames",
    "str text, List[bytes] frames",
    "str text, List[unicode] frames",
    "str text, Tuple[] frames",
    "str text, Tuple[bytes] frames",
    "str text, Tuple[unicode] frames",
]


test_cases = [
    # default frames and interval
    ("", "", None),

    # str text, str frames
    ("Loading", "+x*", 80),

    # unicode text, unicode frames (marked as unicode)
    (u"Загрузка", u"⢄⢂⢁⡁⡈⡐⡠", 80),

    # unicode text, str frames
    ("ℙƴ☂ℌøἤ", "+x*", 80),

    # str text, unicode frames
    ("Loading", "⢄⢂⢁⡁⡈⡐⡠", 80),

    #
    # Iter frames
    #

    # TODO: add custom type that Implements iterable
    #
    # XXX: this is Bad, because different text inputs should
    #      combine with different frames input

    # str text, List[] frames
    ("Empty list", [], 400),

    # str text, List[bytes] frames
    ("Bytes list", [b"\xf0\x9f\x8c\xb2", b"\xf0\x9f\x8e\x84"], 400),

    # str text, List[unicode] frames
    ("Unicode list", [u"🌲", u"🎄"], 400),

    # str text, Tuple[] frames
    ("Empty tuple", (), 400),

    # str text, Tuple[bytes] frames
    ("Bytes tuple", (b"\xf0\x9f\x8c\xb2", b"\xf0\x9f\x8e\x84"), 400),

    # str text, Tuple[unicode] frames
    ("Unicode tuple", (u"🌲", u"🎄"), 400),
]


@pytest.mark.parametrize("spinner, expected", [
    # None
    (None, default_spinner),

    # hasattr(spinner, "frames") and not hasattr(spinner, "interval")
    (namedtuple('Spinner', "frames")("-\\|/"), default_spinner),

    # not hasattr(spinner, "frames") and hasattr(spinner, "interval")
    (namedtuple('Spinner', "interval")(42), default_spinner),

    # Both attrs, not set
    (Spinner("", 0), default_spinner),

    # Both attrs, not frames
    (Spinner("", 42), default_spinner),

    # Both attrs, not interval
    (Spinner("-\\|/", 0), default_spinner),

    # Both attrs, are set
    (Spinner("-\\|/", 42), Spinner("-\\|/", 42)),
])
def test_set_spinner(spinner, expected):
    swirl = yaspin(spinner)
    assert swirl.spinner == expected


@pytest.mark.parametrize("final_text", [
    "", u"",

    "OK", u"OK",

    "✔", u"✔",

    "☀️", u"☀️",

    "💥", u"💥",
])
def test_freeze(final_text):
    swirl = yaspin()
    swirl._freeze(final_text)

    assert isinstance(swirl._last_frame, builtin_str)
    assert swirl._last_frame[-1] == "\n"


def test_ok():
    swirl = yaspin()
    swirl.ok()

    assert isinstance(swirl._last_frame, builtin_str)
    assert swirl._last_frame[-1] == "\n"


def test_fail():
    swirl = yaspin()
    swirl.fail()

    assert isinstance(swirl._last_frame, builtin_str)
    assert swirl._last_frame[-1] == "\n"


#
# Test colors
#
colors_test_cases = [
    # Empty values
    ("", ""),
    (None, None),

    # Supported text colors
    ("red", "red"),
    ("green", "green"),
    ("yellow", "yellow"),
    ("blue", "blue"),
    ("magenta", "magenta"),
    ("cyan", "cyan"),
    ("white", "white"),

    # Unsupported text colors
    ("black", ValueError()),
    ("brown", ValueError()),
    ("orange", ValueError()),

    # Uppercase handling
    ("Red", "red"),
    ("grEEn", "green"),
    ("BlacK", ValueError()),

    # Callables
    (
        lambda frame: colored(frame, 'red', attrs=['bold']),
        lambda frame: colored(frame, 'red', attrs=['bold']),
    )
]


@pytest.mark.parametrize("color, expected", colors_test_cases)
def test_color_argument(color, expected):

    # Exception
    if isinstance(expected, Exception):
        with pytest.raises(type(expected)):
            yaspin(color=color)

    # Callable arg
    elif callable(color):
        # Compare source code to check funcs equality
        fn1 = yaspin(color=color)._color
        fn2 = expected
        assert getsource(fn1) == getsource(fn2)

    # Common arg
    else:
        assert yaspin(color=color)._color == expected


@pytest.mark.parametrize("color, expected", colors_test_cases)
def test_color_property(color, expected):
    swirl = yaspin()

    # Exception
    if isinstance(expected, Exception):
        with pytest.raises(type(expected)):
            swirl.color = color

    # Callable arg
    elif callable(color):
        # Compare source code to check funcs equality
        swirl.color = color
        assert getsource(swirl.color) == getsource(expected)

    # Common arg
    else:
        swirl.color = color
        assert swirl.color == expected


@pytest.mark.parametrize("color, expected", colors_test_cases)
def test_compose_out_with_color(color, expected):
    # Skip non relevant cases
    if not expected:
        return
    if isinstance(expected, Exception):
        return

    # Sanitize input
    if hasattr(color, 'lower'):
        color = color.lower()

    swirl = yaspin(color=color)
    out = swirl._compose_out(frame=u'/')
    assert out.startswith('\r\033')
    assert isinstance(out, builtin_str)


#
# Test right properties
#

@pytest.mark.parametrize("right", [False, True], ids=["left", "right"])
def test_right_property_getter(right):
    swirl = yaspin(right=right)
    assert swirl.right == right


@pytest.mark.parametrize("right", [False, True], ids=["left", "right"])
def test_right_property_setter(right):
    swirl = yaspin()
    swirl.right = right
    assert swirl.right == right


#
# Test reverse properties
#

@pytest.mark.parametrize("reverse", [False, True], ids=["default", "reversed"])
def test_reverse_property_getter(reverse):
    swirl = yaspin(reverse=reverse)
    assert swirl.reverse == reverse


@pytest.mark.parametrize("reverse", [False, True], ids=["default", "reversed"])
def test_reverse_property_setter(reverse):
    swirl = yaspin()
    swirl.reverse = reverse

    assert swirl.reverse == reverse
    assert isinstance(swirl._frames, str)
