from __future__ import (absolute_import, division, print_function)

import six
from six.moves import zip, range
from cycler import cycler, Cycler
from nose.tools import assert_equal, assert_raises
from itertools import product
from operator import add, iadd, mul, imul


def _cycler_helper(c, length, keys, values):
    assert_equal(len(c), length)
    assert_equal(len(c), len(list(c)))
    assert_equal(c.keys, set(keys))

    for k, vals in zip(keys, values):
        for v, v_target in zip(c, vals):
            assert_equal(v[k], v_target)


def _cycles_equal(c1, c2):
    assert_equal(list(c1), list(c2))


def test_creation():
    c = cycler('c', 'rgb')
    yield _cycler_helper, c, 3, ['c'], [['r', 'g', 'b']]
    c = cycler('c', list('rgb'))
    yield _cycler_helper, c, 3, ['c'], [['r', 'g', 'b']]


def test_compose():
    c1 = cycler('c', 'rgb')
    c2 = cycler('lw', range(3))
    c3 = cycler('lw', range(15))
    # addition
    yield _cycler_helper, c1+c2, 3, ['c', 'lw'], [list('rgb'), range(3)]
    yield _cycler_helper, c2+c1, 3, ['c', 'lw'], [list('rgb'), range(3)]
    yield _cycles_equal, c2+c1, c1+c2
    # miss-matched add lengths
    assert_raises(ValueError, add, c1, c3)
    assert_raises(ValueError, add, c3, c1)

    # multiplication
    target = zip(*product(list('rgb'), range(3)))
    yield (_cycler_helper, c1 * c2, 9, ['c', 'lw'], target)

    target = zip(*product(range(3), list('rgb')))
    yield (_cycler_helper, c2 * c1, 9, ['lw', 'c'], target)

    target = zip(*product(range(15), list('rgb')))
    yield (_cycler_helper, c3 * c1, 45, ['lw', 'c'], target)


def test_inplace():
    c1 = cycler('c', 'rgb')
    c2 = cycler('lw', range(3))
    c2 += c1
    yield _cycler_helper, c2, 3, ['c', 'lw'], [list('rgb'), range(3)]

    c3 = cycler('c', 'rgb')
    c4 = cycler('lw', range(3))
    c3 *= c4
    target = zip(*product(list('rgb'), range(3)))
    yield (_cycler_helper, c3, 9, ['c', 'lw'], target)


def test_constructor():
    c1 = cycler('c', 'rgb')
    c2 = cycler('ec', c1)
    yield _cycler_helper, c1+c2, 3, ['c', 'ec'], [['r', 'g', 'b']]*2
    c3 = cycler('c', c1)
    yield _cycler_helper, c3+c2, 3, ['c', 'ec'], [['r', 'g', 'b']]*2


def test_failures():
    c1 = cycler('c', 'rgb')
    c2 = cycler('c', c1)
    assert_raises(ValueError, add, c1, c2)
    assert_raises(ValueError, iadd, c1, c2)
    assert_raises(ValueError, mul, c1, c2)
    assert_raises(ValueError, imul, c1, c2)

    c3 = cycler('ec', c1)

    assert_raises(ValueError, cycler, 'c', c2 + c3)


def test_simplify():
    c1 = cycler('c', 'rgb')
    c2 = cycler('ec', c1)
    for c in [c1 * c2, c2 * c1, c1 + c2]:
        yield _cycles_equal, c, c.simplify()


def test_multiply():
    c1 = cycler('c', 'rgb')
    yield _cycler_helper, 2*c1, 6, ['c'], ['rgb'*2]

    c2 = cycler('ec', c1)
    c3 = c1 * c2

    yield _cycles_equal, 2*c3, c3*2


def test_mul_fails():
    c1 = cycler('c', 'rgb')
    assert_raises(TypeError, mul, c1,  2.0)
    assert_raises(TypeError, mul, c1,  'a')
    assert_raises(TypeError, mul, c1,  [])


def test_getitem():
    c1 = cycler('lw', range(15))
    widths = list(range(15))
    for slc in (slice(None, None, None),
                slice(None, None, -1),
                slice(1, 5, None),
                slice(0, 5, 2)):
        yield _cycles_equal, c1[slc], cycler('lw', widths[slc])


def test_fail_getime():
    c1 = cycler('lw', range(15))
    assert_raises(ValueError, Cycler.__getitem__, c1, 0)
    assert_raises(ValueError, Cycler.__getitem__, c1, [0, 1])


def _repr_tester_helper(rpr_func, cyc, target_repr):
    test_repr = getattr(cyc, rpr_func)()

    assert_equal(six.text_type(test_repr),
                 six.text_type(target_repr))


def test_repr():
    c = cycler('c', 'rgb')
    c2 = cycler('lw', range(3))

    c_sum_rpr = "(cycler('c', ['r', 'g', 'b']) + cycler('lw', [0, 1, 2]))"
    c_prod_rpr = "(cycler('c', ['r', 'g', 'b']) * cycler('lw', [0, 1, 2]))"

    yield _repr_tester_helper, '__repr__', c + c2, c_sum_rpr
    yield _repr_tester_helper, '__repr__', c * c2, c_prod_rpr

    sum_html = "<table><th>'c'</th><th>'lw'</th><tr><td>'r'</td><td>0</td></tr><tr><td>'g'</td><td>1</td></tr><tr><td>'b'</td><td>2</td></tr></table>"
    prod_html = "<table><th>'c'</th><th>'lw'</th><tr><td>'r'</td><td>0</td></tr><tr><td>'r'</td><td>1</td></tr><tr><td>'r'</td><td>2</td></tr><tr><td>'g'</td><td>0</td></tr><tr><td>'g'</td><td>1</td></tr><tr><td>'g'</td><td>2</td></tr><tr><td>'b'</td><td>0</td></tr><tr><td>'b'</td><td>1</td></tr><tr><td>'b'</td><td>2</td></tr></table>"

    yield _repr_tester_helper, '_repr_html_', c + c2, sum_html
    yield _repr_tester_helper, '_repr_html_', c * c2, prod_html
