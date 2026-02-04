
import random
import math

# Hex constants for Types in Gen 1
TYPE_MAP = {
    "NORMAL": 0x00,
    "FIGHTING": 0x01,
    "FLYING": 0x02,
    "POISON": 0x03,
    "GROUND": 0x04,
    "ROCK": 0x05,
    "BUG": 0x07,
    "GHOST": 0x08,
    "FIRE": 0x14,
    "WATER": 0x15,
    "GRASS": 0x16,
    "ELECTRIC": 0x17,
    "PSYCHIC": 0x18,
    "ICE": 0x19,
    "DRAGON": 0x1A
}

# Data Structure: 
# Internal_ID (Decimal): {
#     "name": "Name",
#     "types": [Type1_Hex, Type2_Hex], (If mono-type, Type2 = Type1)
#     "base_stats": { "hp": X, "atk": X, "def": X, "spd": X, "spec": X }
# }
# Note: Gen 1 had "Special" stat, which split into SpAtk/SpDef later. We use 'spec'.

POKEMON_DATA = {
    1:  {"name": "RHYDON",     "types": [0x04, 0x05], "base_stats": {"hp": 105, "atk": 130, "def": 120, "spd": 40, "spec": 45}},
    2:  {"name": "KANGASKHAN", "types": [0x00, 0x00], "base_stats": {"hp": 105, "atk": 95,  "def": 80,  "spd": 90, "spec": 40}},
    3:  {"name": "NIDORAN M",  "types": [0x03, 0x03], "base_stats": {"hp": 46,  "atk": 57,  "def": 40,  "spd": 50, "spec": 40}},
    4:  {"name": "CLEFAIRY",   "types": [0x00, 0x00], "base_stats": {"hp": 70,  "atk": 45,  "def": 48,  "spd": 35, "spec": 60}},
    5:  {"name": "SPEAROW",    "types": [0x00, 0x02], "base_stats": {"hp": 40,  "atk": 60,  "def": 30,  "spd": 70, "spec": 31}},
    6:  {"name": "VOLTORB",    "types": [0x17, 0x17], "base_stats": {"hp": 40,  "atk": 30,  "def": 50,  "spd": 100, "spec": 55}},
    7:  {"name": "NIDOKING",   "types": [0x03, 0x04], "base_stats": {"hp": 81,  "atk": 92,  "def": 77,  "spd": 85, "spec": 75}},
    8:  {"name": "SLOWBRO",    "types": [0x15, 0x18], "base_stats": {"hp": 95,  "atk": 75,  "def": 110, "spd": 30, "spec": 80}},
    9:  {"name": "IVYSAUR",    "types": [0x16, 0x03], "base_stats": {"hp": 60,  "atk": 62,  "def": 63,  "spd": 60, "spec": 80}},
    10: {"name": "EXEGGUTOR",  "types": [0x16, 0x18], "base_stats": {"hp": 95,  "atk": 95,  "def": 85,  "spd": 55, "spec": 125}},
    11: {"name": "LICKITUNG",  "types": [0x00, 0x00], "base_stats": {"hp": 90,  "atk": 55,  "def": 75,  "spd": 30, "spec": 60}},
    12: {"name": "EXEGGCUTE",  "types": [0x16, 0x18], "base_stats": {"hp": 60,  "atk": 40,  "def": 80,  "spd": 40, "spec": 60}},
    13: {"name": "GRIMER",     "types": [0x03, 0x03], "base_stats": {"hp": 80,  "atk": 80,  "def": 50,  "spd": 25, "spec": 40}},
    14: {"name": "GENGAR",     "types": [0x08, 0x03], "base_stats": {"hp": 60,  "atk": 65,  "def": 60,  "spd": 110, "spec": 130}},
    15: {"name": "NIDORAN F",  "types": [0x03, 0x03], "base_stats": {"hp": 55,  "atk": 47,  "def": 52,  "spd": 41, "spec": 40}},
    16: {"name": "NIDOQUEEN",  "types": [0x03, 0x04], "base_stats": {"hp": 90,  "atk": 82,  "def": 87,  "spd": 76, "spec": 75}},
    17: {"name": "CUBONE",     "types": [0x04, 0x04], "base_stats": {"hp": 50,  "atk": 50,  "def": 95,  "spd": 35, "spec": 40}},
    18: {"name": "RHYHORN",    "types": [0x04, 0x05], "base_stats": {"hp": 80,  "atk": 85,  "def": 95,  "spd": 25, "spec": 30}},
    19: {"name": "LAPRAS",     "types": [0x15, 0x19], "base_stats": {"hp": 130, "atk": 85,  "def": 80,  "spd": 60, "spec": 95}},
    20: {"name": "ARCANINE",   "types": [0x14, 0x14], "base_stats": {"hp": 90,  "atk": 110, "def": 80,  "spd": 95, "spec": 80}},
    21: {"name": "MEW",        "types": [0x18, 0x18], "base_stats": {"hp": 100, "atk": 100, "def": 100, "spd": 100, "spec": 100}},
    22: {"name": "GYARADOS",   "types": [0x15, 0x02], "base_stats": {"hp": 95,  "atk": 125, "def": 79,  "spd": 81, "spec": 100}},
    23: {"name": "SHELLDER",   "types": [0x15, 0x15], "base_stats": {"hp": 30,  "atk": 65,  "def": 100, "spd": 40, "spec": 45}},
    24: {"name": "TENTACOOL",  "types": [0x15, 0x03], "base_stats": {"hp": 40,  "atk": 40,  "def": 35,  "spd": 70, "spec": 100}},
    25: {"name": "GASTLY",     "types": [0x08, 0x03], "base_stats": {"hp": 30,  "atk": 35,  "def": 30,  "spd": 80, "spec": 100}},
    26: {"name": "SCYTHER",    "types": [0x07, 0x02], "base_stats": {"hp": 70,  "atk": 110, "def": 80,  "spd": 105, "spec": 55}},
    27: {"name": "STARYU",     "types": [0x15, 0x15], "base_stats": {"hp": 30,  "atk": 45,  "def": 55,  "spd": 85, "spec": 70}},
    28: {"name": "BLASTOISE",  "types": [0x15, 0x15], "base_stats": {"hp": 79,  "atk": 83,  "def": 100, "spd": 78, "spec": 85}},
    29: {"name": "PINSIR",     "types": [0x07, 0x07], "base_stats": {"hp": 65,  "atk": 125, "def": 100, "spd": 85, "spec": 55}},
    30: {"name": "TANGELA",    "types": [0x16, 0x16], "base_stats": {"hp": 65,  "atk": 55,  "def": 115, "spd": 60, "spec": 100}},
    33: {"name": "GROWLITHE",  "types": [0x14, 0x14], "base_stats": {"hp": 55,  "atk": 70,  "def": 45,  "spd": 60, "spec": 50}},
    34: {"name": "ONIX",       "types": [0x05, 0x04], "base_stats": {"hp": 35,  "atk": 45,  "def": 160, "spd": 70, "spec": 30}},
    35: {"name": "FEAROW",     "types": [0x00, 0x02], "base_stats": {"hp": 65,  "atk": 90,  "def": 65,  "spd": 100, "spec": 61}},
    36: {"name": "PIDGEY",     "types": [0x00, 0x02], "base_stats": {"hp": 40,  "atk": 45,  "def": 40,  "spd": 56, "spec": 35}},
    37: {"name": "SLOWPOKE",   "types": [0x15, 0x18], "base_stats": {"hp": 90,  "atk": 65,  "def": 65,  "spd": 15, "spec": 40}},
    38: {"name": "KADABRA",    "types": [0x18, 0x18], "base_stats": {"hp": 40,  "atk": 35,  "def": 30,  "spd": 105, "spec": 120}},
    39: {"name": "GRAVELER",   "types": [0x05, 0x04], "base_stats": {"hp": 55,  "atk": 95,  "def": 115, "spd": 35, "spec": 45}},
    40: {"name": "CHANSEY",    "types": [0x00, 0x00], "base_stats": {"hp": 250, "atk": 5,   "def": 5,   "spd": 50, "spec": 105}},
    41: {"name": "MACHOKE",    "types": [0x01, 0x01], "base_stats": {"hp": 80,  "atk": 100, "def": 70,  "spd": 45, "spec": 50}},
    42: {"name": "MR. MIME",   "types": [0x18, 0x18], "base_stats": {"hp": 40,  "atk": 45,  "def": 65,  "spd": 90, "spec": 100}},
    43: {"name": "HITMONLEE",  "types": [0x01, 0x01], "base_stats": {"hp": 50,  "atk": 120, "def": 53,  "spd": 87, "spec": 35}},
    44: {"name": "HITMONCHAN", "types": [0x01, 0x01], "base_stats": {"hp": 50,  "atk": 105, "def": 79,  "spd": 76, "spec": 35}},
    45: {"name": "ARBOK",      "types": [0x03, 0x03], "base_stats": {"hp": 60,  "atk": 85,  "def": 69,  "spd": 80, "spec": 65}},
    46: {"name": "PARASECT",   "types": [0x07, 0x16], "base_stats": {"hp": 60,  "atk": 95,  "def": 80,  "spd": 30, "spec": 80}},
    47: {"name": "PSYDUCK",    "types": [0x15, 0x15], "base_stats": {"hp": 50,  "atk": 52,  "def": 48,  "spd": 55, "spec": 50}},
    48: {"name": "DROWZEE",    "types": [0x18, 0x18], "base_stats": {"hp": 60,  "atk": 48,  "def": 45,  "spd": 42, "spec": 90}},
    49: {"name": "GOLEM",      "types": [0x05, 0x04], "base_stats": {"hp": 80,  "atk": 110, "def": 130, "spd": 45, "spec": 55}},
    51: {"name": "MAGMAR",     "types": [0x14, 0x14], "base_stats": {"hp": 65,  "atk": 95,  "def": 57,  "spd": 93, "spec": 85}},
    53: {"name": "ELECTABUZZ", "types": [0x17, 0x17], "base_stats": {"hp": 65,  "atk": 83,  "def": 57,  "spd": 105, "spec": 85}},
    54: {"name": "MAGNETON",   "types": [0x17, 0x17], "base_stats": {"hp": 50,  "atk": 60,  "def": 95,  "spd": 70, "spec": 120}},
    55: {"name": "KOFFING",    "types": [0x03, 0x03], "base_stats": {"hp": 40,  "atk": 65,  "def": 95,  "spd": 35, "spec": 60}},
    57: {"name": "MANKEY",     "types": [0x01, 0x01], "base_stats": {"hp": 40,  "atk": 80,  "def": 35,  "spd": 70, "spec": 35}},
    58: {"name": "SEEL",       "types": [0x15, 0x15], "base_stats": {"hp": 65,  "atk": 45,  "def": 55,  "spd": 45, "spec": 70}},
    59: {"name": "DIGLETT",    "types": [0x04, 0x04], "base_stats": {"hp": 10,  "atk": 55,  "def": 25,  "spd": 95, "spec": 45}},
    60: {"name": "TAUROS",     "types": [0x00, 0x00], "base_stats": {"hp": 75,  "atk": 100, "def": 95,  "spd": 110, "spec": 70}},
    64: {"name": "FARFETCH'D", "types": [0x00, 0x02], "base_stats": {"hp": 52,  "atk": 65,  "def": 55,  "spd": 60, "spec": 58}},
    65: {"name": "VENONAT",    "types": [0x07, 0x03], "base_stats": {"hp": 60,  "atk": 55,  "def": 50,  "spd": 45, "spec": 40}},
    66: {"name": "DRAGONITE",  "types": [0x1A, 0x02], "base_stats": {"hp": 91,  "atk": 134, "def": 95,  "spd": 80, "spec": 100}},
    70: {"name": "DODUO",      "types": [0x00, 0x02], "base_stats": {"hp": 35,  "atk": 85,  "def": 45,  "spd": 75, "spec": 35}},
    71: {"name": "POLIWAG",    "types": [0x15, 0x15], "base_stats": {"hp": 40,  "atk": 50,  "def": 40,  "spd": 90, "spec": 40}},
    72: {"name": "JYNX",       "types": [0x19, 0x18], "base_stats": {"hp": 65,  "atk": 50,  "def": 35,  "spd": 95, "spec": 95}},
    73: {"name": "MOLTRES",    "types": [0x14, 0x02], "base_stats": {"hp": 90,  "atk": 100, "def": 90,  "spd": 90, "spec": 125}},
    74: {"name": "ARTICUNO",   "types": [0x19, 0x02], "base_stats": {"hp": 90,  "atk": 85,  "def": 100, "spd": 85, "spec": 125}},
    75: {"name": "ZAPDOS",     "types": [0x17, 0x02], "base_stats": {"hp": 90,  "atk": 90,  "def": 85,  "spd": 100, "spec": 125}},
    76: {"name": "DITTO",      "types": [0x00, 0x00], "base_stats": {"hp": 48,  "atk": 48,  "def": 48,  "spd": 48, "spec": 48}},
    77: {"name": "MEOWTH",     "types": [0x00, 0x00], "base_stats": {"hp": 40,  "atk": 45,  "def": 35,  "spd": 90, "spec": 40}},
    78: {"name": "KRABBY",     "types": [0x15, 0x15], "base_stats": {"hp": 30,  "atk": 105, "def": 90,  "spd": 50, "spec": 25}},
    82: {"name": "VULPIX",     "types": [0x14, 0x14], "base_stats": {"hp": 38,  "atk": 41,  "def": 40,  "spd": 65, "spec": 65}},
    83: {"name": "NINETALES",  "types": [0x14, 0x14], "base_stats": {"hp": 73,  "atk": 76,  "def": 75,  "spd": 100, "spec": 100}},
    84: {"name": "PIKACHU",    "types": [0x17, 0x17], "base_stats": {"hp": 35,  "atk": 55,  "def": 30,  "spd": 90, "spec": 50}},
    85: {"name": "RAICHU",     "types": [0x17, 0x17], "base_stats": {"hp": 60,  "atk": 90,  "def": 55,  "spd": 100, "spec": 90}},
    88: {"name": "DRATINI",    "types": [0x1A, 0x1A], "base_stats": {"hp": 41,  "atk": 64,  "def": 45,  "spd": 50, "spec": 50}},
    89: {"name": "DRAGONAIR",  "types": [0x1A, 0x1A], "base_stats": {"hp": 61,  "atk": 84,  "def": 65,  "spd": 70, "spec": 70}},
    90: {"name": "KABUTO",     "types": [0x05, 0x15], "base_stats": {"hp": 30,  "atk": 80,  "def": 90,  "spd": 55, "spec": 45}},
    91: {"name": "KABUTOPS",   "types": [0x05, 0x15], "base_stats": {"hp": 60,  "atk": 115, "def": 105, "spd": 80, "spec": 70}},
    92: {"name": "HORSEA",     "types": [0x15, 0x15], "base_stats": {"hp": 30,  "atk": 40,  "def": 70,  "spd": 60, "spec": 70}},
    93: {"name": "SEADRA",     "types": [0x15, 0x15], "base_stats": {"hp": 55,  "atk": 65,  "def": 95,  "spd": 85, "spec": 95}},
    96: {"name": "SANDSHREW",  "types": [0x04, 0x04], "base_stats": {"hp": 50,  "atk": 75,  "def": 85,  "spd": 40, "spec": 30}},
    97: {"name": "SANDSLASH",  "types": [0x04, 0x04], "base_stats": {"hp": 75,  "atk": 100, "def": 110, "spd": 65, "spec": 55}},
    98: {"name": "OMANYTE",    "types": [0x05, 0x15], "base_stats": {"hp": 35,  "atk": 40,  "def": 100, "spd": 35, "spec": 90}},
    99: {"name": "OMASTAR",    "types": [0x05, 0x15], "base_stats": {"hp": 70,  "atk": 60,  "def": 125, "spd": 55, "spec": 115}},
    100: {"name": "JIGGLYPUFF","types": [0x00, 0x00], "base_stats": {"hp": 115, "atk": 45,  "def": 20,  "spd": 20, "spec": 25}},
    101: {"name": "WIGGLYTUFF","types": [0x00, 0x00], "base_stats": {"hp": 140, "atk": 70,  "def": 45,  "spd": 45, "spec": 50}},
    102: {"name": "EEVEE",     "types": [0x00, 0x00], "base_stats": {"hp": 55,  "atk": 55,  "def": 50,  "spd": 55, "spec": 65}},
    103: {"name": "FLAREON",   "types": [0x14, 0x14], "base_stats": {"hp": 65,  "atk": 130, "def": 60,  "spd": 65, "spec": 110}},
    104: {"name": "JOLTEON",   "types": [0x17, 0x17], "base_stats": {"hp": 65,  "atk": 65,  "def": 60,  "spd": 130, "spec": 110}},
    105: {"name": "VAPOREON",  "types": [0x15, 0x15], "base_stats": {"hp": 130, "atk": 65,  "def": 60,  "spd": 65, "spec": 110}},
    106: {"name": "MACHOP",    "types": [0x01, 0x01], "base_stats": {"hp": 70,  "atk": 80,  "def": 50,  "spd": 35, "spec": 35}},
    107: {"name": "ZUBAT",     "types": [0x03, 0x02], "base_stats": {"hp": 40,  "atk": 45,  "def": 35,  "spd": 55, "spec": 40}},
    108: {"name": "EKANS",     "types": [0x03, 0x03], "base_stats": {"hp": 35,  "atk": 60,  "def": 44,  "spd": 55, "spec": 40}},
    109: {"name": "PARAS",     "types": [0x07, 0x16], "base_stats": {"hp": 35,  "atk": 70,  "def": 55,  "spd": 25, "spec": 55}},
    110: {"name": "POLIWHIRL", "types": [0x15, 0x15], "base_stats": {"hp": 65,  "atk": 65,  "def": 65,  "spd": 90, "spec": 50}},
    111: {"name": "POLIWRATH", "types": [0x15, 0x01], "base_stats": {"hp": 90,  "atk": 85,  "def": 95,  "spd": 70, "spec": 70}},
    112: {"name": "WEEDLE",    "types": [0x07, 0x03], "base_stats": {"hp": 40,  "atk": 35,  "def": 30,  "spd": 50, "spec": 20}},
    113: {"name": "KAKUNA",    "types": [0x07, 0x03], "base_stats": {"hp": 45,  "atk": 25,  "def": 50,  "spd": 35, "spec": 25}},
    114: {"name": "BEEDRILL",  "types": [0x07, 0x03], "base_stats": {"hp": 65,  "atk": 80,  "def": 40,  "spd": 75, "spec": 45}},
    115: {"name": "DODRIO",    "types": [0x00, 0x02], "base_stats": {"hp": 60,  "atk": 110, "def": 70,  "spd": 100, "spec": 60}},
    116: {"name": "PRIMEAPE",  "types": [0x01, 0x01], "base_stats": {"hp": 65,  "atk": 105, "def": 60,  "spd": 95, "spec": 60}},
    117: {"name": "DUGTRIO",   "types": [0x04, 0x04], "base_stats": {"hp": 35,  "atk": 80,  "def": 50,  "spd": 120, "spec": 70}},
    118: {"name": "VENOMOTH",  "types": [0x07, 0x03], "base_stats": {"hp": 70,  "atk": 65,  "def": 60,  "spd": 90, "spec": 90}},
    119: {"name": "DEWGONG",   "types": [0x15, 0x19], "base_stats": {"hp": 90,  "atk": 70,  "def": 80,  "spd": 70, "spec": 95}},
    121: {"name": "CATERPIE",  "types": [0x07, 0x07], "base_stats": {"hp": 45,  "atk": 30,  "def": 35,  "spd": 45, "spec": 20}},
    122: {"name": "METAPOD",   "types": [0x07, 0x07], "base_stats": {"hp": 50,  "atk": 20,  "def": 55,  "spd": 30, "spec": 25}},
    123: {"name": "BUTTERFREE","types": [0x07, 0x02], "base_stats": {"hp": 60,  "atk": 45,  "def": 50,  "spd": 70, "spec": 80}},
    124: {"name": "MACHAMP",   "types": [0x01, 0x01], "base_stats": {"hp": 90,  "atk": 130, "def": 80,  "spd": 55, "spec": 65}},
    125: {"name": "CLOYSTER",  "types": [0x15, 0x19], "base_stats": {"hp": 50,  "atk": 95,  "def": 180, "spd": 70, "spec": 85}},
    126: {"name": "GOLDUCK",   "types": [0x15, 0x15], "base_stats": {"hp": 80,  "atk": 82,  "def": 78,  "spd": 85, "spec": 80}},
    127: {"name": "HYPNO",     "types": [0x18, 0x18], "base_stats": {"hp": 85,  "atk": 73,  "def": 70,  "spd": 67, "spec": 115}},
    128: {"name": "GOLBAT",    "types": [0x03, 0x02], "base_stats": {"hp": 75,  "atk": 80,  "def": 70,  "spd": 90, "spec": 75}},
    129: {"name": "MEWTWO",    "types": [0x18, 0x18], "base_stats": {"hp": 106, "atk": 110, "def": 90,  "spd": 130, "spec": 154}},
    130: {"name": "SNORLAX",   "types": [0x00, 0x00], "base_stats": {"hp": 160, "atk": 110, "def": 65,  "spd": 30, "spec": 65}},
    131: {"name": "MAGIKARP",  "types": [0x15, 0x15], "base_stats": {"hp": 20,  "atk": 10,  "def": 55,  "spd": 80, "spec": 20}},
    132: {"name": "MUK",       "types": [0x03, 0x03], "base_stats": {"hp": 105, "atk": 105, "def": 75,  "spd": 50, "spec": 65}},
    136: {"name": "KINGLER",   "types": [0x15, 0x15], "base_stats": {"hp": 55,  "atk": 130, "def": 115, "spd": 75, "spec": 50}},
    138: {"name": "SLOWPOKE",  "types": [0x15, 0x18], "base_stats": {"hp": 90,  "atk": 65,  "def": 65,  "spd": 15, "spec": 40}}, 
    139: {"name": "IVYSAUR",   "types": [0x16, 0x03], "base_stats": {"hp": 60,  "atk": 62,  "def": 63,  "spd": 60, "spec": 80}}, # Dupe ID?
    142: {"name": "ELECTRODE", "types": [0x17, 0x17], "base_stats": {"hp": 60,  "atk": 50,  "def": 70,  "spd": 140, "spec": 80}},
    143: {"name": "CLEFABLE",  "types": [0x00, 0x00], "base_stats": {"hp": 95,  "atk": 70,  "def": 73,  "spd": 60, "spec": 85}},
    144: {"name": "WEEZING",   "types": [0x03, 0x03], "base_stats": {"hp": 65,  "atk": 90,  "def": 120, "spd": 60, "spec": 85}},
    145: {"name": "PERSIAN",   "types": [0x00, 0x00], "base_stats": {"hp": 65,  "atk": 70,  "def": 60,  "spd": 115, "spec": 65}},
    146: {"name": "MAROWAK",   "types": [0x04, 0x04], "base_stats": {"hp": 60,  "atk": 80,  "def": 110, "spd": 45, "spec": 50}},
    148: {"name": "HAUNTER",   "types": [0x08, 0x03], "base_stats": {"hp": 45,  "atk": 50,  "def": 45,  "spd": 95, "spec": 115}},
    149: {"name": "ABRA",      "types": [0x18, 0x18], "base_stats": {"hp": 25,  "atk": 20,  "def": 15,  "spd": 90, "spec": 105}},
    150: {"name": "ALAKAZAM",  "types": [0x18, 0x18], "base_stats": {"hp": 55,  "atk": 50,  "def": 45,  "spd": 120, "spec": 135}},
    151: {"name": "PIDGEOTTO", "types": [0x00, 0x02], "base_stats": {"hp": 63,  "atk": 60,  "def": 55,  "spd": 71, "spec": 50}},
    152: {"name": "PIDGEOT",   "types": [0x00, 0x02], "base_stats": {"hp": 83,  "atk": 80,  "def": 75,  "spd": 91, "spec": 70}},
    153: {"name": "STARMIE",   "types": [0x15, 0x18], "base_stats": {"hp": 60,  "atk": 75,  "def": 85,  "spd": 115, "spec": 100}},
    154: {"name": "BULBASAUR", "types": [0x16, 0x03], "base_stats": {"hp": 45,  "atk": 49,  "def": 49,  "spd": 45, "spec": 65}},
    155: {"name": "VENUSAUR",  "types": [0x16, 0x03], "base_stats": {"hp": 80,  "atk": 82,  "def": 83,  "spd": 80, "spec": 100}},
    156: {"name": "TENTACRUEL","types": [0x15, 0x03], "base_stats": {"hp": 80,  "atk": 70,  "def": 65,  "spd": 100, "spec": 120}},
    158: {"name": "GOLDEEN",   "types": [0x15, 0x15], "base_stats": {"hp": 45,  "atk": 67,  "def": 60,  "spd": 63, "spec": 50}},
    159: {"name": "SEAKING",   "types": [0x15, 0x15], "base_stats": {"hp": 80,  "atk": 92,  "def": 65,  "spd": 68, "spec": 80}},
    163: {"name": "PONYTA",    "types": [0x14, 0x14], "base_stats": {"hp": 50,  "atk": 85,  "def": 55,  "spd": 90, "spec": 65}},
    164: {"name": "RAPIDASH",  "types": [0x14, 0x14], "base_stats": {"hp": 65,  "atk": 100, "def": 70,  "spd": 105, "spec": 80}},
    165: {"name": "RATTATA",   "types": [0x00, 0x00], "base_stats": {"hp": 30,  "atk": 56,  "def": 35,  "spd": 72, "spec": 25}},
    166: {"name": "RATICATE",  "types": [0x00, 0x00], "base_stats": {"hp": 55,  "atk": 81,  "def": 60,  "spd": 97, "spec": 50}},
    167: {"name": "NIDORINO",  "types": [0x03, 0x03], "base_stats": {"hp": 61,  "atk": 72,  "def": 57,  "spd": 65, "spec": 55}},
    168: {"name": "NIDORINA",  "types": [0x03, 0x03], "base_stats": {"hp": 70,  "atk": 62,  "def": 67,  "spd": 56, "spec": 55}},
    169: {"name": "GEODUDE",   "types": [0x05, 0x04], "base_stats": {"hp": 40,  "atk": 80,  "def": 100, "spd": 20, "spec": 30}},
    170: {"name": "PORYGON",   "types": [0x00, 0x00], "base_stats": {"hp": 65,  "atk": 60,  "def": 70,  "spd": 40, "spec": 75}},
    171: {"name": "AERODACTYL","types": [0x05, 0x02], "base_stats": {"hp": 80,  "atk": 105, "def": 65,  "spd": 130, "spec": 60}},
    173: {"name": "MAGNEMITE", "types": [0x17, 0x17], "base_stats": {"hp": 25,  "atk": 35,  "def": 70,  "spd": 45, "spec": 95}},
    176: {"name": "CHARMANDER","types": [0x14, 0x14], "base_stats": {"hp": 39,  "atk": 52,  "def": 43,  "spd": 65, "spec": 50}},
    177: {"name": "SQUIRTLE",  "types": [0x15, 0x15], "base_stats": {"hp": 44,  "atk": 48,  "def": 65,  "spd": 43, "spec": 50}},
    178: {"name": "CHARMELEON","types": [0x14, 0x14], "base_stats": {"hp": 58,  "atk": 64,  "def": 58,  "spd": 80, "spec": 65}},
    179: {"name": "WARTORTLE", "types": [0x15, 0x15], "base_stats": {"hp": 59,  "atk": 63,  "def": 80,  "spd": 58, "spec": 65}},
    180: {"name": "CHARIZARD", "types": [0x14, 0x02], "base_stats": {"hp": 78,  "atk": 84,  "def": 78,  "spd": 100, "spec": 85}},
    185: {"name": "ODDISH",    "types": [0x16, 0x03], "base_stats": {"hp": 45,  "atk": 50,  "def": 55,  "spd": 30, "spec": 75}},
    186: {"name": "GLOOM",     "types": [0x16, 0x03], "base_stats": {"hp": 60,  "atk": 65,  "def": 70,  "spd": 40, "spec": 85}},
    187: {"name": "VILEPLUME", "types": [0x16, 0x03], "base_stats": {"hp": 75,  "atk": 80,  "def": 85,  "spd": 50, "spec": 100}},
    188: {"name": "BELLSPROUT","types": [0x16, 0x03], "base_stats": {"hp": 50,  "atk": 75,  "def": 35,  "spd": 40, "spec": 70}},
    189: {"name": "WEEPINBELL","types": [0x16, 0x03], "base_stats": {"hp": 65,  "atk": 90,  "def": 50,  "spd": 55, "spec": 85}},
    190: {"name": "VICTREEBEL","types": [0x16, 0x03], "base_stats": {"hp": 80,  "atk": 105, "def": 65,  "spd": 70, "spec": 100}}
}

# Add missing IDs or clean up duplicates in a real scenario
valid_ids = list(POKEMON_DATA.keys())

def get_random_level():
    return random.randint(5, 100)

def calculate_stat(base, iv, level, is_hp=False):
    # Gen 1 Formula
    # HP = ((( (Base + IV) * 2 ) * Level) / 100 ) + Level + 10
    # Other = ((( (Base + IV) * 2 ) * Level) / 100 ) + 5
    # EV usually adds sqrt(EV)/4 but we assume 0 EV for simplicity
    
    core = (base + iv) * 2
    val = math.floor((core * level) / 100)
    
    if is_hp:
        return val + level + 10
    else:
        return val + 5

def get_random_pokemon(level):
    species_id = random.choice(valid_ids)
    p_data = POKEMON_DATA[species_id]
    
    # Generate random IVs (0-15) for DVs
    # In Gen 1, HP IV is determined by the last bit of Atk, Def, Spd, Spec IVs
    iv_atk = random.randint(0, 15)
    iv_def = random.randint(0, 15)
    iv_spd = random.randint(0, 15)
    iv_spec = random.randint(0, 15)
    
    iv_hp = ((iv_atk & 1) << 3) | ((iv_def & 1) << 2) | ((iv_spd & 1) << 1) | (iv_spec & 1)
    
    stats = {}
    stats['hp'] = calculate_stat(p_data['base_stats']['hp'], iv_hp, level, is_hp=True)
    stats['atk'] = calculate_stat(p_data['base_stats']['atk'], iv_atk, level)
    stats['def'] = calculate_stat(p_data['base_stats']['def'], iv_def, level)
    stats['spd'] = calculate_stat(p_data['base_stats']['spd'], iv_spd, level)
    stats['spec'] = calculate_stat(p_data['base_stats']['spec'], iv_spec, level) # Use for both sp_atk/sp_def in gen 1 logic if needed, but RAM splits them usually or uses same? In Gen 1 RAM D02B is Special.
    
    # Moves: Random 1-165
    moves = [random.randint(1, 165) for _ in range(4)]
    
    return {
        "species_id": species_id,
        "types": p_data['types'],
        "stats": stats,
        "max_hp": stats['hp'],
        "moves": moves,
        "name": p_data['name']
    }

MOVES_MAP = {
    "POUND": 0x01, "KARATE CHOP": 0x02, "DOUBLESLAP": 0x03, "COMET PUNCH": 0x04, "MEGA PUNCH": 0x05,
    "PAY DAY": 0x06, "FIRE PUNCH": 0x07, "ICE PUNCH": 0x08, "THUNDERPUNCH": 0x09, "SCRATCH": 0x0A,
    "VICEGRIP": 0x0B, "GUILLOTINE": 0x0C, "RAZOR WIND": 0x0D, "SWORDS DANCE": 0x0E, "CUT": 0x0F,
    "GUST": 0x10, "WING ATTACK": 0x11, "WHIRLWIND": 0x12, "FLY": 0x13, "BIND": 0x14,
    "SLAM": 0x15, "VINE WHIP": 0x16, "STOMP": 0x17, "DOUBLE KICK": 0x18, "MEGA KICK": 0x19,
    "JUMP KICK": 0x1A, "ROLLING KICK": 0x1B, "SAND ATTACK": 0x1C, "HEADBUTT": 0x1D, "HORN ATTACK": 0x1E,
    "FURY ATTACK": 0x1F, "HORN DRILL": 0x20, "TACKLE": 0x21, "BODY SLAM": 0x22, "WRAP": 0x23,
    "TAKE DOWN": 0x24, "THRASH": 0x25, "DOUBLE-EDGE": 0x26, "TAIL WHIP": 0x27, "POISON STING": 0x28,
    "TWINEEDLE": 0x29, "PIN MISSILE": 0x2A, "LEER": 0x2B, "BITE": 0x2C, "GROWL": 0x2D,
    "ROAR": 0x2E, "SING": 0x2F, "SUPERSONIC": 0x30, "SONICBOOM": 0x31, "DISABLE": 0x32,
    "ACID": 0x33, "EMBER": 0x34, "FLAMETHROWER": 0x35, "MIST": 0x36, "WATER GUN": 0x37,
    "HYDRO PUMP": 0x38, "SURF": 0x39, "ICE BEAM": 0x3A, "BLIZZARD": 0x3B, "PSYBEAM": 0x3C,
    "BUBBLEBEAM": 0x3D, "AURORA BEAM": 0x3E, "HYPER BEAM": 0x3F, "PECK": 0x40, "DRILL PECK": 0x41,
    "SUBMISSION": 0x42, "LOW KICK": 0x43, "COUNTER": 0x44, "SEISMIC TOSS": 0x45, "STRENGTH": 0x46,
    "ABSORB": 0x47, "MEGA DRAIN": 0x48, "LEECH SEED": 0x49, "GROWTH": 0x4A, "RAZOR LEAF": 0x4B,
    "SOLARBEAM": 0x4C, "POISONPOWDER": 0x4D, "STUN SPORE": 0x4E, "SLEEP POWDER": 0x4F, "PETAL DANCE": 0x50,
    "STRING SHOT": 0x51, "DRAGON RAGE": 0x52, "FIRE SPIN": 0x53, "THUNDERSHOCK": 0x54, "THUNDERBOLT": 0x55,
    "THUNDER WAVE": 0x56, "THUNDER": 0x57, "ROCK THROW": 0x58, "EARTHQUAKE": 0x59, "FISSURE": 0x5A,
    "DIG": 0x5B, "TOXIC": 0x5C, "CONFUSION": 0x5D, "PSYCHIC": 0x5E, "HYPNOSIS": 0x5F,
    "MEDITATE": 0x60, "AGILITY": 0x61, "QUICK ATTACK": 0x62, "RAGE": 0x63, "TELEPORT": 0x64,
    "NIGHT SHADE": 0x65, "MIMIC": 0x66, "SCREECH": 0x67, "DOUBLE TEAM": 0x68, "RECOVER": 0x69,
    "HARDEN": 0x6A, "MINIMIZE": 0x6B, "SMOKESCREEN": 0x6C, "CONFUSE RAY": 0x6D, "WITHDRAW": 0x6E,
    "DEFENSE CURL": 0x6F, "BARRIER": 0x70, "LIGHT SCREEN": 0x71, "HAZE": 0x72, "REFLECT": 0x73,
    "FOCUS ENERGY": 0x74, "BIDE": 0x75, "METRONOME": 0x76, "MIRROR MOVE": 0x77, "SELFDESTRUCT": 0x78,
    "EGG BOMB": 0x79, "LICK": 0x7A, "SMOG": 0x7B, "SLUDGE": 0x7C, "BONE CLUB": 0x7D,
    "FIRE BLAST": 0x7E, "WATERFALL": 0x7F, "CLAMP": 0x80, "SWIFT": 0x81, "SKULL BASH": 0x82,
    "SPIKE CANNON": 0x83, "CONSTRICT": 0x84, "AMNESIA": 0x85, "KINESIS": 0x86, "SOFTBOILED": 0x87,
    "HI JUMP KICK": 0x88, "GLARE": 0x89, "DREAM EATER": 0x8A, "POISON GAS": 0x8B, "BARRAGE": 0x8C,
    "LEECH LIFE": 0x8D, "LOVELY KISS": 0x8E, "SKY ATTACK": 0x8F, "TRANSFORM": 0x90, "BUBBLE": 0x91,
    "DIZZY PUNCH": 0x92, "SPORE": 0x93, "FLASH": 0x94, "PSYWAVE": 0x95, "SPLASH": 0x96,
    "ACID ARMOR": 0x97, "CRABHAMMER": 0x98, "EXPLOSION": 0x99, "FURY SWIPES": 0x9A, "BONEMERANG": 0x9B,
    "REST": 0x9C, "ROCK SLIDE": 0x9D, "HYPER FANG": 0x9E, "SHARPEN": 0x9F, "CONVERSION": 0xA0,
    "TRI ATTACK": 0xA1, "SUPER FANG": 0xA2, "SLASH": 0xA3, "SUBSTITUTE": 0xA4, "STRUGGLE": 0xA5
}
