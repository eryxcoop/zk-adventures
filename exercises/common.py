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


class Domain:
    def __init__(self, omega: int):
        """Produces the set of all powers of `omega` modulo `p` and stores them in `self._elements`"""
        omega = F(omega)
        size = omega.multiplicative_order()
        self._elements = [omega ** i for i in range(size)]
    
    @classmethod
    def of_size(cls, size: int):
        """Returns a domain of size `size`."""
        # generator of the full units group of 𝔽. That is, the powers 
        # of `generator` produce all nonzero elements of 𝔽
        generator = F.multiplicative_generator()
        p = F.order()
        if size <= 0 or (p - 1) % size != 0:
            raise ValueError
        omega = int(generator ** ((p - 1) // size))
        return cls(omega)
    
    def __len__(self):
        return len(self._elements)
    
    def __getitem__(self, index):
        return self._elements[index]


class Oracle:
    def __init__(self, polynomial: Polynomial):
        raise NotImplementedError("subclass responsibility")
        
    def query(self, z):
        raise NotImplementedError("subclass responsibility")

import sys

class NaiveOracle(Oracle):
    def __init__(self, polynomial: Polynomial):
        self._polynomial = polynomial
    
    def query(self, z):
        """
        One-time single use function. Returns the value of the polynomial at `z`.
        On first use this function dumps the polynomial and returns `None`
        for subsequent calls.
        """
        if self._polynomial is not None:
            y = self._polynomial(z)
            self._polynomial = None
            return y

