from collections import Sequence, Mapping, OrderedDict
from functools import singledispatch

D, L, I, E, C = b'dlie:'


# Encode

def _compound(type_, seq, out):
    out.append(type_)
    for e in seq:
        encoder(e, out)
    out.append(E)


def _flat(m):
    for k, v in sorted(m.items()):
        yield k
        yield v


@singledispatch
def encoder(a, out):
    raise NotImplemented('Not implemented for ' + type(a))


@encoder.register(int)
def i(i, out):
    out.append(I)
    out.extend(str(i).encode())
    out.append(E)


@encoder.register(bytes)
def b(b, out):
    out.extend(str(len(b)).encode())
    out.append(C)
    out.extend(b)


@encoder.register(str)
def s(s, out):
    encoder(s.encode(), out)


@encoder.register(Sequence)
def l(seq, out):
    _compound(L, seq, out)


@encoder.register(Mapping)
def d(map_, out):
    _compound(D, _flat(map_), out)


def encode(v):
    out = bytearray()
    encoder(v, out)
    return bytes(out)


# Decode

def parse_int(bs, i, char):
    j = bs.index(char, i)
    res = int(bs[i:j].decode())
    return res, j+1


def parse_str(bs, i):
    len_, i = parse_int(bs, i, C)
    j = i + len_
    return bs[i:j], j


def parse_seq(bs, i):
    l = []
    while True:
        v, i = parse(bs, i)
        if v == E:
            return l, i
        else:
            l.append(v)


def parse_dict(bs, i):
    seq, i = parse_seq(bs, i)
    if len(seq) % 2 != 0:
        raise ValueError('Unexpected end of a dictionary')
    if not all(isinstance(k, bytes) for k in seq[::2]):
        raise ValueError('Dictionary key should be "bytes" instance')
    return OrderedDict(zip(*[iter(seq)]*2)), i


def parse(bs, i):
    c = bs[i]
    if c == E:
        return E, i+1
    elif c == D:
        return parse_dict(bs, i+1)
    elif c == L:
        return parse_seq(bs, i+1)
    elif c == I:
        return parse_int(bs, i+1, E)
    else:  # assume string
        return parse_str(bs, i)


def decode(bs):
    res, _ = parse(bs, 0)
    return res
