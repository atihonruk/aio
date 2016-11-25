from functools import singledispatch
from collections import Sequence, Mapping

D, L, I, E, C = b'dlie:'


# Encode

def _compound(seq, type_, out):
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
def l(l, out):
    _compound(l, L, out)


@encoder.register(Mapping)
def d(m, out):
    _compound(_flat(m), D, out)


def encode(v):
    out = bytearray()
    encoder(v, out)
    return bytes(out)


# Decode

def get_int(bs, i, char):
    j = bs.index(char, i)
    res = int(bs[i:j].decode())
    return res, j+1


def get_str(bs, i):
    len_, i = get_int(bs, i, C)
    j = i + len_
    return bs[i:j], j


def get_list(bs, i):
    l = []
    while True:
        v, i = parse(bs, i)
        if v == E:
            return l, i
        else:
            l.append(v)


def get_dict(bs, i):
    d = {}
    while True:
        k, i = parse(bs, i)
        if k == E:
            return d, i
        elif not isinstance(k, bytes):
            raise ValueError('Dictionary key should be "bytes" instance, got {} instead'
                             .format(type(k)))
        else:
            v, i = parse(bs, i)
            if v == E:
                raise ValueError('Unexpected end of a dictionary')
            d[k] = v


def parse(bs, i):
    c = bs[i]
    if c == E:
        return E, i+1
    elif c == D:
        return get_dict(bs, i+1)
    elif c == L:
        return get_list(bs, i+1)
    elif c == I:
        return get_int(bs, i+1, E)
    else:  # assume string
        return get_str(bs, i)


def decode(bs):
    res, _ = parse(bs, 0)
    return res
