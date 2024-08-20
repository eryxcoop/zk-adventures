from hashlib import sha3_256
from zk_adventures_types import F, Polynomial

X = Polynomial.monomial(1)

### solutions/1_fiat_shamir_schnorr.sage ####

class Transcript:
    def __init__(self, initialization_bytes: bytes):
        raise NotImplementedError("subclass responsibility")
        
    def append(self, bytes_to_append: bytes):
        raise NotImplementedError("subclass responsibility")
    
    def sample(self) -> bytes:
        raise NotImplementedError("subclass responsibility")


class Sha3_256Transcript(Transcript):
    def __init__(self, initialization_bytes: bytes):
        """Creates a new SHA3-256 hasher. Initializes it with `initialization_bytes`"""
        self.hasher = sha3_256()
        self.hasher.update(initialization_bytes)
        
    def append(self, bytes_to_append: bytes):
        """Updates the hasher with `bytes_to_append`"""
        self.hasher.update(bytes_to_append)

    def sample(self) -> bytes:
        """
        The return value is the digest of the hasher.
        Replaces the hasher with a fresh new one and initialized
        with the return value of this function
        """
        result = self.hasher.digest()
        self.hasher = sha3_256()
        self.hasher.update(result)
        return result
