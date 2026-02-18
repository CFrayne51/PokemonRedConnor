import numpy as np
from .constants import (
    HP_ADDRS, MAX_HP_ADDRS, ENEMY_HP_ADDRS, ENEMY_MAX_HP_ADDRS, 
    ENEMY_PARTY_COUNT, PARTY_SIZE_ADDR, PARTY_LEVEL_ADDRS, PARTY_TYPE_ADDRS
)

class PyBoyMemory:
    def __init__(self, pyboy):
        self.pyboy = pyboy

    def read_m(self, addr):
        return self.pyboy.memory[addr]

    def read_bit(self, addr, bit: int) -> bool:
        # add padding so zero will read '0b100000000' instead of '0b0'
        return bin(256 + self.read_m(addr))[-bit - 1] == "1"

    def read_short(self, start_addr):
        return 256 * self.read_m(start_addr) + self.read_m(start_addr + 1)

    def read_hp_fraction(self):
        hp_sum = sum([self.read_short(add) for add in HP_ADDRS])
        max_hp_sum = sum([self.read_short(add) for add in MAX_HP_ADDRS])
        max_hp_sum = max(max_hp_sum, 1)
        return hp_sum / max_hp_sum

    def read_enemy_hp_fraction(self):
        # Number of enemy Pokémon in the party
        n = int(self.read_m(ENEMY_PARTY_COUNT))
        n = max(1, min(n, 6)) # Clamp to 1-6

        hp_sum = sum(self.read_short(a) for a in ENEMY_HP_ADDRS[:n])
        max_hp_sum = sum(self.read_short(a) for a in ENEMY_MAX_HP_ADDRS[:n])
        max_hp_sum = max(max_hp_sum, 1)
        return hp_sum / max_hp_sum

    def read_party(self):
        return [self.read_m(addr) for addr in PARTY_TYPE_ADDRS]
    
    def read_party_levels(self):
        return [self.read_m(addr) for addr in PARTY_LEVEL_ADDRS]
    
    def read_party_size(self):
        return self.read_m(PARTY_SIZE_ADDR)
