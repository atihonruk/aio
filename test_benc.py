from benc import encode, decode


class TestBencode:
    """http://www.bittorrent.org/beps/bep_0003.html"""

    def test_string(self):
        # Strings are length-prefixed base ten followed by a colon and the string.
        # For example 4:spam corresponds to 'spam'.
        assert decode(encode('spam')) == b'spam'

    def test_integer(self):
        # Integers are represented by an 'i' followed by the number in base 10 followed by an 'e'.
        # For example i3e corresponds to 3 and i-3e corresponds to -3.
        assert decode(encode(3)) == 3
        assert decode(encode(-3)) == -3
        # Integers have no size limitation. i-0e is invalid.
        # All encodings with a leading zero, such as i03e, are invalid,
        # other than i0e, which of course corresponds to 0.
        assert decode(encode(0)) == 0

    def test_list(self):
        # Lists are encoded as an 'l' followed by their elements (also bencoded) followed by an 'e'.
        # For example l4:spam4:eggse corresponds to ['spam', 'eggs'].
        assert decode(encode(['spam', 'eggs'])) == [b'spam', b'eggs']

    def test_dict(self):
        # Dictionaries are encoded as a 'd' followed by a list of alternating keys
        # and their corresponding values followed by an 'e'.
        # For example, d3:cow3:moo4:spam4:eggse corresponds to {'cow': 'moo', 'spam': 'eggs'}
        assert decode(encode({'cow': 'moo', 'spam': 'eggs'})) == {b'cow': b'moo', b'spam': b'eggs'}
        # and d4:spaml1:a1:bee corresponds to {'spam': ['a', 'b']}.
        assert decode(encode({'spam': ['a', 'b']})) == {b'spam': [b'a', b'b']}
        # Keys must be strings and appear in sorted order (sorted as raw strings, not alphanumerics).
