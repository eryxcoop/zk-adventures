from dataclasses import dataclass
from hashlib import sha3_256
from enum import IntEnum
from zk_adventures_types import F, Polynomial, CURVE_GENERATOR as G, CURVE_NEUTRAL_ELEMENT as O, pairing, E
from typing import List, Set
from kzg_srs import SRS

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


class Equation:
    """An expression of form Q_L X + Q_R Y + Q_M X Y + Q_O Z + Q_C on variables X, Y and Z"""
    def __init__(self, Q_L: int, Q_R: int, Q_M: int, Q_O: int, Q_C: int):
        self._values = (F(Q_L), F(Q_R), F(Q_M), F(Q_O), F(Q_C))
        
    def values(self):
        return self._values
        
    def __getitem__(self, index):
        if not isinstance(index, self.Index):
            raise ValueError
        return self._values[index]
    
    class Index(IntEnum):
        L = 0, 
        R = 1,
        M = 2,
        O = 3,
        C = 4

class Triplet:
    """A triplet of values (A, B, C) in the finite field"""
    def __init__(self, A: int, B: int, C: int):
        self._values = (F(A), F(B), F(C))
    
    def values(self):
        return self._values
        
    def __getitem__(self, index):
        if not isinstance(index, self.Index):
            raise ValueError
        return self._values[index]

    class Index(IntEnum):
        A = 0, 
        B = 1,
        C = 2

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

def interpolate_triplets(domain: Domain, triplets: list[Triplet], index: Triplet.Index) -> Polynomial:
    """Returns the polynomial `p` such that `p(domain[i]) = triplets[i][index]"""
    values = [triplet[index] for triplet in triplets]
    return Polynomial.lagrange_polynomial(list(zip(domain, values)))

def interpolate_equations(domain: Domain, equations: list[Equation], index: Equation.Index) -> Polynomial:
    """Returns the polynomial `p` such that `p(domain[i]) = equation[i][index]"""
    values = [equation[index] for equation in equations]
    return Polynomial.lagrange_polynomial(list(zip(domain, values)))

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

### solutions/3_plonk_wiring_satisfiability_with_oracles.sage ####


def construct_Z_polynomial(V: List[int], W: List[int], random_coeff: int, domain: Domain):
    """
    Returns the polynomial Z of least degree such that
        * Z(1) = 1, and
        * Z(𝜔ⁱ) = ((V₀ + 𝛼)⋅⋅⋅(Vᵢ₋₁ + a)) / ((Wₒ + 𝛼)⋅⋅⋅(Wᵢ₋₁ + 𝛼)), for all i = 1, ..., N-1, 
    where 𝛼 is `random_coeff`, 𝜔 is `domain[1]` and N is the size of `domain`
    """
    cumulative_product = F(1)
    cumulative_products = [cumulative_product]
    for v, w in zip(V[:-1], W[:-1]):
        cumulative_product *= (F(v) + random_coeff) / (F(w) + random_coeff)
        cumulative_products.append(cumulative_product)   
    return Polynomial.lagrange_polynomial(zip(domain, cumulative_products))

import ctypes

def interpolate_values(domain: Domain, values: List[int]) -> Polynomial:
    return Polynomial.lagrange_polynomial(zip(domain, values))


