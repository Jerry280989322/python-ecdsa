
import binascii
from hashlib import sha256, sha512
import der
from curves import orderlen

# RFC5480:
#   The "unrestricted" algorithm identifier is:
#     id-ecPublicKey OBJECT IDENTIFIER ::= {
#       iso(1) member-body(2) us(840) ansi-X9-62(10045) keyType(2) 1 }

oid_ecPublicKey = (1, 2, 840, 10045, 2, 1)
encoded_oid_ecPublicKey = der.encode_oid(*oid_ecPublicKey)

class PRNG:
    # this returns a callable which, when invoked with an integer N, will
    # return N pseudorandom bytes.
    def __init__(self, seed):
        self.generator = self.block_generator(seed)

    def __call__(self, numbytes):
        return "".join([self.generator.next() for i in range(numbytes)])

    def block_generator(self, seed):
        counter = 0
        while True:
            for byte in sha256("prng-%d-%s" % (counter, seed)).digest():
                yield byte
            counter += 1

def string_to_randrange(seed, order):
    # hash the data, then turn the digest into a number in [1,order).
    #
    # We use David-Sarah Hopwood's suggestion: turn it into a number that's
    # sufficiently larger than the group order, then modulo it down to fit.
    # This should give adequate (but not perfect) uniformity, and simple
    # code. There are other choices: try-try-again is the main one.
    base = PRNG(seed)(2*orderlen(order))
    number = (int(binascii.hexlify(base), 16) % (order-1)) + 1
    assert 1 <= number < order, (1, number, order)
    return number

def string_to_randrange_truncate(data, order):
    # hash the data, then turn the digest into a number in [1,order), but
    # don't worry about trying to uniformly fill the range
    base = PRNG(seed)(len("%x" % order))
    number = (int(binascii.hexlify(base), 16) % (order-1)) + 1
    assert 1 <= number < order, (1, number, order)
    return number

    h = 4*sha512(data).hexdigest()
    olen = len("%x" % order)
    assert len(h) > 2*olen, (len(h), olen)
    number = (int(h, 16) % (order-1)) + 1
    assert 1 <= number < order, (1, number, order)
    return number

def OLDstring_to_randrange_truncate(data, order):
    # hash the data, then turn the digest into a number in [1,order), but
    # don't worry about trying to uniformly fill the range
    h = 4*sha512(data).hexdigest()
    olen = len("%x" % order)
    assert len(h) > 2*olen, (len(h), olen)
    number = (int(h, 16) % (order-1)) + 1
    assert 1 <= number < order, (1, number, order)
    return number

def number_to_string(num, order):
    l = orderlen(order)
    fmt_str = "%0" + str(2*l) + "x"
    string = binascii.unhexlify(fmt_str % num)
    assert len(string) == l, (len(string), l)
    return string

def hashfunc_truncate(hashclass):
    def hashfunc(string, order):
        h = hashclass(string).digest()
        h = "\x00"*(orderlen(order)-len(h)) + h # pad to size
        number = string_to_number(h, order)
        return number
    return hashfunc

def string_to_number(string, order):
    l = orderlen(order)
    assert len(string) == l, (len(string), l)
    return int(binascii.hexlify(string), 16)

def sig_to_strings(r, s, order):
    r_str = number_to_string(r, order)
    s_str = number_to_string(s, order)
    return (r_str, s_str)

def sig_to_string(r, s, order):
    # for any given curve, the size of the signature numbers is
    # fixed, so just use simple concatenation
    r_str, s_str = sig_to_strings(r, s, order)
    return r_str + s_str

def sig_to_der(r, s, order):
    return der.encode_sequence(der.encode_integer(r), der.encode_integer(s))


def infunc_string(signature, order):
    l = orderlen(order)
    assert len(signature) == 2*l, (len(signature), 2*l)
    r = string_to_number(signature[:l], order)
    s = string_to_number(signature[l:], order)
    return r, s

def infunc_strings((r_str, s_str), order):
    l = orderlen(order)
    assert len(r_str) == l, (len(r_str), l)
    assert len(s_str) == l, (len(s_str), l)
    r = string_to_number(r_str, order)
    s = string_to_number(s_str, order)
    return r, s

def infunc_der(sig_der, order):
    #return der.encode_sequence(der.encode_integer(r), der.encode_integer(s))
    rs_strings, empty = der.remove_sequence(sig_der)
    if empty != "":
        raise der.UnexpectedDER("trailing junk after DER sig: %s" %
                                binascii.hexlify(empty))
    r, rest = der.remove_integer(rs_strings)
    s, empty = der.remove_integer(rest)
    if empty != "":
        raise der.UnexpectedDER("trailing junk after DER numbers: %s" %
                                binascii.hexlify(empty))
    return r, s

