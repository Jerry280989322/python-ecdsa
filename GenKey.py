# -*- coding:utf-8 -*-
"""generate public key on NIST256p"""
"""
1.G/Q-check
    /ecdas/ellipticcurve.py
    class CurveFp()
        ...
        def contains_point(self,x,y)
        ...
    class Point()
        ...
            if self.__curve:
            assert self.__curve.contains_point(x, y)   #comment this func out to avoid the G-check
        ...

"""
from ecdsa import SigningKey, NIST256p

sk = SigningKey.generate(curve=NIST256p)
vk = sk.get_verifying_key()

sk_pem = sk.to_pem()
vk_pem = vk.to_pem()
print(sk_pem)
print(vk_pem)

signature = sk.sign("message")
assert vk.verify(signature, "message")  #验签通过则无输出，否则报错