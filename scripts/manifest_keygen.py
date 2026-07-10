#!/usr/bin/env python3
"""Generate an Ed25519 keypair for optional manifest signing.

Requires PyNaCl:

    python3 -m pip install pynacl
    python3 scripts/manifest_keygen.py

Set the private key as ARCADE_MANIFEST_SIGNING_KEY only on the release runner.
Bake the public key into ARCADE_MANIFEST_PUBKEY or the loader constant once
ready to enforce signatures.
"""
import base64

from nacl.signing import SigningKey

key = SigningKey.generate()
print("ARCADE_MANIFEST_SIGNING_KEY=" + base64.b64encode(bytes(key)).decode())
print("ARCADE_MANIFEST_PUBKEY=" + base64.b64encode(bytes(key.verify_key)).decode())
