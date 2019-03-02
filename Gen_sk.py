"""
Generate a fixed sk(private key)
"""

from ecdsa import SigningKey, NIST256p
import json

'''generate the sk and save it to skfile.json'''

sk = SigningKey.generate(curve=NIST256p) #generate a random sk
sk_pem = sk.to_pem()                     #transform it into PEM format

skfile='skfile.json'
with open(skfile,'w') as f_obj:
    json.dump(sk_pem,f_obj)

print(sk_pem)