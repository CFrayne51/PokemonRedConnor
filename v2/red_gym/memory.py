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
        n = int(self.read_m(0xD89C)) # ENEMY_PARTY_COUNT
        n = max(1, min(n, 6)) # Clamp to 1-6

        hp_sum = sum(self.read_short(a) for a in ENEMY_HP_ADDRS[:n])
        max_hp_sum = sum(self.read_short(a) for a in ENEMY_MAX_HP_ADDRS[:n])
        max_hp_sum = max(max_hp_sum, 1)
        
        # print(f"[DEBUG-MEM] E-Party Count: {n}, HP Sum: {hp_sum}, MaxHP Sum: {max_hp_sum}")
        return hp_sum / max_hp_sum

    def read_party(self):
        return [self.read_m(addr) for addr in PARTY_TYPE_ADDRS]
    
    def read_party_levels(self):
        return [self.read_m(addr) for addr in PARTY_LEVEL_ADDRS]
    
    def read_party_size(self):
        return self.read_m(PARTY_SIZE_ADDR)

    def write_m(self, addr, val):
        self.pyboy.memory[addr] = val

    def inject_ram(self):
        from . import pokemon_data
        level = pokemon_data.get_random_level()

        def write_mon_data(start_addr, p_data):
            # Species (1 byte)
            self.write_m(start_addr, p_data['species_id'])
            # HP (2 bytes)
            self.write_m(start_addr + 1, (p_data['max_hp'] >> 8) & 0xFF)
            self.write_m(start_addr + 2, p_data['max_hp'] & 0xFF)
            # Level (1 byte) - Note: In party mon, Level is at offset 33 (start+33)
            # but in wBattleMon it's elsewhere. This helper is for PartyMon structure.
            # PartyMon structure: Species(1), HP(2), Level(1), Status(1), Type1(1), Type2(1), ...
            # Actually, standard Gen 1 PartyMon (44 bytes):
            # 0: species, 1-2: HP, 3: Level (box), 4: Status, 5-6: Types, 7: Catch rate/Item, 8-11: Moves, 12-13: OT ID, 14-16: Exp, 17-18: HP EV, ...
            # 33: Level, 34-35: Max HP, 36-37: Atk, 38-39: Def, 40-41: Spd, 42-43: Spec
            self.write_m(start_addr + 33, level)
            self.write_m(start_addr + 34, (p_data['max_hp'] >> 8) & 0xFF)
            self.write_m(start_addr + 35, p_data['max_hp'] & 0xFF)
            self.write_m(start_addr + 36, (p_data['stats']['atk'] >> 8) & 0xFF)
            self.write_m(start_addr + 37, p_data['stats']['atk'] & 0xFF)
            self.write_m(start_addr + 38, (p_data['stats']['def'] >> 8) & 0xFF)
            self.write_m(start_addr + 39, p_data['stats']['def'] & 0xFF)
            self.write_m(start_addr + 40, (p_data['stats']['spd'] >> 8) & 0xFF)
            self.write_m(start_addr + 41, p_data['stats']['spd'] & 0xFF)
            self.write_m(start_addr + 42, (p_data['stats']['spec'] >> 8) & 0xFF)
            self.write_m(start_addr + 43, p_data['stats']['spec'] & 0xFF)
            # Moves (4 bytes at offset 8)
            for i, move_id in enumerate(p_data['moves']):
                self.write_m(start_addr + 8 + i, move_id)
            # Types (2 bytes at offset 5)
            self.write_m(start_addr + 5, p_data['types'][0])
            self.write_m(start_addr + 6, p_data['types'][1])

        # 1. Player Party (wPartyMon1-6)
        player_party = [pokemon_data.get_random_pokemon(level) for _ in range(6)]
        self.write_m(0xD163, 6) # wPartyCount
        for i, p_data in enumerate(player_party):
            self.write_m(0xD164 + i, p_data['species_id']) # wPartySpecies
            write_mon_data(0xD16B + (i * 44), p_data)
        self.write_m(0xD164 + 6, 0xFF) # Terminator

        # Sync Active Player Mon (wBattleMon)
        p0 = player_party[0]
        self.write_m(0xD014, p0['species_id'])
        self.write_m(0xD015, (p0['max_hp'] >> 8) & 0xFF) # Current HP
        self.write_m(0xD016, p0['max_hp'] & 0xFF)
        self.write_m(0xD019, p0['types'][0])
        self.write_m(0xD01A, p0['types'][1])
        for i, move_id in enumerate(p0['moves']):
            self.write_m(0xD01C + i, move_id)
        self.write_m(0xD022, level)
        self.write_m(0xD023, (p0['max_hp'] >> 8) & 0xFF) # Max HP
        self.write_m(0xD024, p0['max_hp'] & 0xFF)
        self.write_m(0xD025, (p0['stats']['atk'] >> 8) & 0xFF)
        self.write_m(0xD026, p0['stats']['atk'] & 0xFF)
        self.write_m(0xD027, (p0['stats']['def'] >> 8) & 0xFF)
        self.write_m(0xD028, p0['stats']['def'] & 0xFF)
        self.write_m(0xD029, (p0['stats']['spd'] >> 8) & 0xFF)
        self.write_m(0xD02A, p0['stats']['spd'] & 0xFF)
        self.write_m(0xD02B, (p0['stats']['spec'] >> 8) & 0xFF)
        self.write_m(0xD02C, p0['stats']['spec'] & 0xFF)

        # 2. Enemy Party (wEnemyMon1-6)
        enemy_party = [pokemon_data.get_random_pokemon(level) for _ in range(6)]
        self.write_m(0xD89C, 6) # wEnemyPartyCount
        for i, e_data in enumerate(enemy_party):
            self.write_m(0xD89D + i, e_data['species_id']) # wEnemyPartySpecies
            write_mon_data(0xD8A4 + (i * 44), e_data)
        self.write_m(0xD89D + 6, 0xFF) # Terminator

        # Sync Active Enemy Mon (wEnemyMon)
        e0 = enemy_party[0]
        self.write_m(0xCFE5, e0['species_id'])
        self.write_m(0xCFE6, (e0['max_hp'] >> 8) & 0xFF) # Current HP
        self.write_m(0xCFE7, e0['max_hp'] & 0xFF)
        self.write_m(0xCFEA, e0['types'][0])
        self.write_m(0xCFEB, e0['types'][1])
        for i, move_id in enumerate(e0['moves']):
            self.write_m(0xCFED + i, move_id)
        self.write_m(0xCFF3, level)
        self.write_m(0xCFF4, (e0['max_hp'] >> 8) & 0xFF) # Max HP
        self.write_m(0xCFF5, e0['max_hp'] & 0xFF)
        self.write_m(0xCFF6, (e0['stats']['atk'] >> 8) & 0xFF)
        self.write_m(0xCFF7, e0['stats']['atk'] & 0xFF)
        self.write_m(0xCFF8, (e0['stats']['def'] >> 8) & 0xFF)
        self.write_m(0xCFF9, e0['stats']['def'] & 0xFF)
        self.write_m(0xCFFA, (e0['stats']['spd'] >> 8) & 0xFF)
        self.write_m(0xCFFB, e0['stats']['spd'] & 0xFF)
        self.write_m(0xCFFC, (e0['stats']['spec'] >> 8) & 0xFF)
        self.write_m(0xCFFD, e0['stats']['spec'] & 0xFF)

    def get_pos(self):
        from .constants import X_POS_ADDR, Y_POS_ADDR, MAP_N_ADDR
        return (
            self.read_m(X_POS_ADDR),
            self.read_m(Y_POS_ADDR),
            self.read_m(MAP_N_ADDR)
        )

    def read_moves(self):
        # wBattleMonMoves = 0xD01C (4 bytes)
        return [self.read_m(0xD01C + i) for i in range(4)]

    def read_enemy_moves(self):
        # wEnemyMonMoves = 0xCFED (4 bytes)
        return [self.read_m(0xCFED + i) for i in range(4)]
