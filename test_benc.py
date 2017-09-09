from hypothesis import given, example
from hypothesis.strategies import binary,\
    dictionaries, integers, lists, one_of, recursive, text

from benc import encode, decode


"""http://www.bittorrent.org/beps/bep_0003.html"""


SIMPlE_TYPES = one_of(integers(), binary())


# Strings are length-prefixed base ten followed by a colon and the string.
# For example 4:spam corresponds to 'spam'.
@given(text())
@example('spam')
def test_string(s):
    assert decode(encode(s)) == bytes(s, 'utf-8')


@given(binary())
def test_bytestring(s):
    assert decode(encode(s)) == s


# Integers are represented by an 'i' followed by the number in base 10 followed by an 'e'.
# For example i3e corresponds to 3 and i-3e corresponds to -3.
# Integers have no size limitation. i-0e is invalid.
# All encodings with a leading zero, such as i03e, are invalid,
# other than i0e, which of course corresponds to 0.
@given(integers())
@example(3)
@example(-3)
@example(0)
def test_integer(i):
    assert decode(encode(i)) == i


# Lists are encoded as an 'l' followed by their elements (also bencoded) followed by an 'e'.
# For example l4:spam4:eggse corresponds to ['spam', 'eggs'].
@given(recursive(SIMPLE_TYPES, lists))
@example([b'spam', b'eggs'])
def test_list(l):
    assert decode(encode(l)) == l


# Dictionaries are encoded as a 'd' followed by a list of alternating keys
# and their corresponding values followed by an 'e'.
# For example, d3:cow3:moo4:spam4:eggse corresponds to {'cow': 'moo', 'spam': 'eggs'}
@given(recursive(SIMPLE_TYPES,
                 lambda t: dictionaries(binary(), one_of(lists(t), t))))
@example({b'cow': b'moo', b'spam': b'eggs'})
@example({b'spam': [b'a', b'b']})
def test_dict(d):
    assert decode(encode(d)) == d

# TODO
# Keys must be strings and appear in sorted order (sorted as raw strings, not alphanumerics).
