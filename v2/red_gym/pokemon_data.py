
import random
import math

# Hex constants for Types in Gen 1
TYPE_MAP = {
    "NORMAL": 0x00, "FIGHTING": 0x01, "FLYING": 0x02, "POISON": 0x03, "GROUND": 0x04,
    "ROCK": 0x05, "BUG": 0x07, "GHOST": 0x08, "FIRE": 0x14, "WATER": 0x15,
    "GRASS": 0x16, "ELECTRIC": 0x17, "PSYCHIC": 0x18, "ICE": 0x19, "DRAGON": 0x1A
}

# Key Pokemon for Randomized Battles
POKEMON_DATA = {
    1:  {"name": "RHYDON",     "types": [0x04, 0x05], "base_stats": {"hp": 105, "atk": 130, "def": 120, "spd": 40, "spec": 45}},
    7:  {"name": "NIDOKING",   "types": [0x03, 0x04], "base_stats": {"hp": 81,  "atk": 92,  "def": 77,  "spd": 85, "spec": 75}},
    14: {"name": "GENGAR",     "types": [0x08, 0x03], "base_stats": {"hp": 60,  "atk": 65,  "def": 60,  "spd": 110, "spec": 130}},
    28: {"name": "BLASTOISE",  "types": [0x15, 0x15], "base_stats": {"hp": 79,  "atk": 83,  "def": 100, "spd": 78, "spec": 85}},
    66: {"name": "DRAGONITE",  "types": [0x1A, 0x02], "base_stats": {"hp": 91,  "atk": 134, "def": 95,  "spd": 80, "spec": 100}},
    103: {"name": "FLAREON",   "types": [0x14, 0x14], "base_stats": {"hp": 65,  "atk": 130, "def": 60,  "spd": 65, "spec": 110}},
    104: {"name": "JOLTEON",   "types": [0x17, 0x17], "base_stats": {"hp": 65,  "atk": 65,  "def": 60,  "spd": 130, "spec": 110}},
    105: {"name": "VAPOREON",  "types": [0x15, 0x15], "base_stats": {"hp": 130, "atk": 65,  "def": 60,  "spd": 65, "spec": 110}},
    129: {"name": "MEWTWO",    "types": [0x18, 0x18], "base_stats": {"hp": 106, "atk": 110, "def": 90,  "spd": 130, "spec": 154}},
    130: {"name": "SNORLAX",   "types": [0x00, 0x00], "base_stats": {"hp": 160, "atk": 110, "def": 65,  "spd": 30, "spec": 65}},
    149: {"name": "ABRA",      "types": [0x18, 0x18], "base_stats": {"hp": 25,  "atk": 20,  "def": 15,  "spd": 90, "spec": 105}},
    155: {"name": "VENUSAUR",  "types": [0x16, 0x03], "base_stats": {"hp": 80,  "atk": 82,  "def": 83,  "spd": 80, "spec": 100}},
    180: {"name": "CHARIZARD", "types": [0x14, 0x02], "base_stats": {"hp": 78,  "atk": 84,  "def": 78,  "spd": 100, "spec": 85}},
}

MOVES_MAP = {
    "POUND": 0x01, "KARATE CHOP": 0x02, "DOUBLESLAP": 0x03, "COMET PUNCH": 0x04, "MEGA PUNCH": 0x05,
    "PAY DAY": 0x06, "FIRE PUNCH": 0x07, "ICE PUNCH": 0x08, "THUNDERPUNCH": 0x09, "SCRATCH": 0x0A,
    "CUT": 0x0F, "GUST": 0x10, "FLY": 0x13, "STOMP": 0x17, "BODY SLAM": 0x22, "DOUBLE-EDGE": 0x26,
    "EMBER": 0x34, "FLAMETHROWER": 0x35, "WATER GUN": 0x37, "HYDRO PUMP": 0x38, "SURF": 0x39,
    "ICE BEAM": 0x3A, "BLIZZARD": 0x3B, "PSYBEAM": 0x3C, "BUBBLEBEAM": 0x3D, "HYPER BEAM": 0x3F,
    "SOLARBEAM": 0x4C, "THUNDERSHOCK": 0x54, "THUNDERBOLT": 0x55, "THUNDER": 0x57, "EARTHQUAKE": 0x59,
    "PSYCHIC": 0x5E, "QUICK ATTACK": 0x62, "NIGHT SHADE": 0x65, "SELFDESTRUCT": 0x78, "FIRE BLAST": 0x7E,
    "SWIFT": 0x81, "SOFTBOILED": 0x87, "DREAM EATER": 0x8A, "EXPLOSION": 0x99, "ROCK SLIDE": 0x9D,
    "TRI-ATTACK": 0xA1, "SLASH": 0xA3, "SUBSTITUTE": 0xA4, "STRUGGLE": 0xA5
}

def get_random_level():
    return random.randint(5, 100)

def calculate_stat(base, iv, level, is_hp=False):
    core = (base + iv) * 2
    val = math.floor((core * level) / 100)
    if is_hp:
        return val + level + 10
    else:
        return val + 5

def get_random_pokemon(level):
    species_id = random.choice(list(POKEMON_DATA.keys()))
    p_data = POKEMON_DATA[species_id]
    
    iv_atk = random.randint(0, 15)
    iv_def = random.randint(0, 15)
    iv_spd = random.randint(0, 15)
    iv_spec = random.randint(0, 15)
    iv_hp = ((iv_atk & 1) << 3) | ((iv_def & 1) << 2) | ((iv_spd & 1) << 1) | (iv_spec & 1)
    
    stats = {
        'hp': calculate_stat(p_data['base_stats']['hp'], iv_hp, level, is_hp=True),
        'atk': calculate_stat(p_data['base_stats']['atk'], iv_atk, level),
        'def': calculate_stat(p_data['base_stats']['def'], iv_def, level),
        'spd': calculate_stat(p_data['base_stats']['spd'], iv_spd, level),
        'spec': calculate_stat(p_data['base_stats']['spec'], iv_spec, level),
    }
    
    # Random Moves from constants above
    moves = [random.choice(list(MOVES_MAP.values())) for _ in range(4)]
    
    return {
        "species_id": species_id,
        "types": p_data['types'],
        "stats": stats,
        "max_hp": stats['hp'],
        "moves": moves,
        "name": p_data['name']
    }
