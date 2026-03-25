
import random
import math

# Hex constants for Types in Gen 1
TYPE_MAP = {
    "NORMAL": 0x00, "FIGHTING": 0x01, "FLYING": 0x02, "POISON": 0x03, "GROUND": 0x04,
    "ROCK": 0x05, "BUG": 0x07, "GHOST": 0x08, "FIRE": 0x14, "WATER": 0x15,
    "GRASS": 0x16, "ELECTRIC": 0x17, "PSYCHIC": 0x18, "ICE": 0x19, "DRAGON": 0x1A
}

# Key Pokemon for Randomized Battles (35 entries)
POKEMON_DATA = {
    0x01: {"name": "RHYDON",     "types": [0x04, 0x05], "base_stats": {"hp": 105, "atk": 130, "def": 120, "spd": 40, "spec": 45}},
    0x02: {"name": "KANGASKHAN", "types": [0x00, 0x00], "base_stats": {"hp": 105, "atk": 95,  "def": 80,  "spd": 90, "spec": 40}},
    0x03: {"name": "NIDORAN_M",  "types": [0x03, 0x03], "base_stats": {"hp": 46,  "atk": 57,  "def": 40,  "spd": 50, "spec": 40}},
    0x04: {"name": "CLEFAIRY",   "types": [0x00, 0x00], "base_stats": {"hp": 70,  "atk": 45,  "def": 48,  "spd": 35, "spec": 60}},
    0x05: {"name": "SPEAROW",    "types": [0x00, 0x02], "base_stats": {"hp": 40,  "atk": 60,  "def": 30,  "spd": 70, "spec": 31}},
    0x06: {"name": "VOLTORB",    "types": [0x17, 0x17], "base_stats": {"hp": 40,  "atk": 30,  "def": 50,  "spd": 100, "spec": 55}},
    0x07: {"name": "NIDOKING",   "types": [0x03, 0x04], "base_stats": {"hp": 81,  "atk": 92,  "def": 77,  "spd": 85, "spec": 75}},
    0x08: {"name": "SLOWBRO",    "types": [0x15, 0x18], "base_stats": {"hp": 95,  "atk": 75,  "def": 110, "spd": 30, "spec": 80}},
    0x09: {"name": "IVYSAUR",    "types": [0x16, 0x03], "base_stats": {"hp": 60,  "atk": 62,  "def": 63,  "spd": 60, "spec": 80}},
    0x0A: {"name": "EXEGGUTOR",  "types": [0x16, 0x18], "base_stats": {"hp": 95,  "atk": 95,  "def": 85,  "spd": 55, "spec": 125}},
    0x0B: {"name": "LICKITUNG",  "types": [0x00, 0x00], "base_stats": {"hp": 90,  "atk": 55,  "def": 75,  "spd": 30, "spec": 60}},
    0x0C: {"name": "EXEGGCUTE",  "types": [0x16, 0x18], "base_stats": {"hp": 60,  "atk": 40,  "def": 80,  "spd": 40, "spec": 60}},
    0x0D: {"name": "GRIMER",     "types": [0x03, 0x03], "base_stats": {"hp": 80,  "atk": 80,  "def": 50,  "spd": 25, "spec": 40}},
    0x0E: {"name": "GENGAR",     "types": [0x08, 0x03], "base_stats": {"hp": 60,  "atk": 65,  "def": 60,  "spd": 110, "spec": 130}},
    0x0F: {"name": "NIDORAN_F",  "types": [0x03, 0x03], "base_stats": {"hp": 55,  "atk": 47,  "def": 52,  "spd": 41, "spec": 40}},
    0x10: {"name": "NIDOQUEEN",  "types": [0x03, 0x04], "base_stats": {"hp": 90,  "atk": 82,  "def": 87,  "spd": 76, "spec": 75}},
    0x11: {"name": "CUBONE",     "types": [0x04, 0x04], "base_stats": {"hp": 50,  "atk": 50,  "def": 95,  "spd": 35, "spec": 40}},
    0x12: {"name": "RHYHORN",    "types": [0x04, 0x05], "base_stats": {"hp": 80,  "atk": 85,  "def": 95,  "spd": 25, "spec": 30}},
    0x13: {"name": "LAPRAS",     "types": [0x15, 0x19], "base_stats": {"hp": 130, "atk": 85,  "def": 80,  "spd": 60, "spec": 95}},
    0x14: {"name": "ARCANINE",   "types": [0x14, 0x14], "base_stats": {"hp": 90,  "atk": 110, "def": 80,  "spd": 95, "spec": 80}},
    0x15: {"name": "MEW",        "types": [0x18, 0x18], "base_stats": {"hp": 100, "atk": 100, "def": 100, "spd": 100, "spec": 100}},
    0x16: {"name": "GYARADOS",   "types": [0x15, 0x02], "base_stats": {"hp": 95,  "atk": 125, "def": 79,  "spd": 81, "spec": 100}},
    0x17: {"name": "SHELLDER",   "types": [0x15, 0x15], "base_stats": {"hp": 30,  "atk": 65,  "def": 100, "spd": 40, "spec": 45}},
    0x18: {"name": "TENTACOOL",  "types": [0x15, 0x03], "base_stats": {"hp": 40,  "atk": 40,  "def": 35,  "spd": 70, "spec": 100}},
    0x19: {"name": "GASTLY",     "types": [0x08, 0x03], "base_stats": {"hp": 30,  "atk": 35,  "def": 30,  "spd": 80, "spec": 100}},
    0x1A: {"name": "SCYTHER",    "types": [0x07, 0x02], "base_stats": {"hp": 70,  "atk": 110, "def": 80,  "spd": 105, "spec": 55}},
    0x1B: {"name": "STARYU",     "types": [0x15, 0x15], "base_stats": {"hp": 30,  "atk": 45,  "def": 55,  "spd": 85, "spec": 70}},
    0x1C: {"name": "BLASTOISE",  "types": [0x15, 0x15], "base_stats": {"hp": 79,  "atk": 83,  "def": 100, "spd": 78, "spec": 85}},
    0x1D: {"name": "PINSIR",     "types": [0x07, 0x07], "base_stats": {"hp": 65,  "atk": 125, "def": 100, "spd": 85, "spec": 55}},
    0x1E: {"name": "TANGELA",    "types": [0x16, 0x16], "base_stats": {"hp": 65,  "atk": 55,  "def": 115, "spd": 60, "spec": 100}},
    0x1F: {"name": "GROWLITHE",  "types": [0x14, 0x14], "base_stats": {"hp": 55,  "atk": 70,  "def": 45,  "spd": 60, "spec": 50}},
    0x20: {"name": "ONIX",       "types": [0x04, 0x05], "base_stats": {"hp": 35,  "atk": 45,  "def": 160, "spd": 70, "spec": 30}},
    0x21: {"name": "FEAROW",     "types": [0x00, 0x02], "base_stats": {"hp": 65,  "atk": 90,  "def": 65,  "spd": 100, "spec": 61}},
    0x22: {"name": "PIDGEY",     "types": [0x00, 0x02], "base_stats": {"hp": 40,  "atk": 45,  "def": 40,  "spd": 56, "spec": 35}},
    0x23: {"name": "SLOWPOKE",   "types": [0x15, 0x18], "base_stats": {"hp": 90,  "atk": 65,  "def": 65,  "spd": 15, "spec": 40}},
}

MOVES_MAP = {
    "POUND": 0x01, "KARATE CHOP": 0x02, "DOUBLESLAP": 0x03, "COMET PUNCH": 0x04, "MEGA PUNCH": 0x05,
    "PAY DAY": 0x06, "FIRE PUNCH": 0x07, "ICE PUNCH": 0x08, "THUNDERPUNCH": 0x09, "SCRATCH": 0x0A,
    "VICEGRIP": 0x0B, "GUILLOTINE": 0x0C, "RAZOR WIND": 0x0D, "SWORDS DANCE": 0x0E, "CUT": 0x0F,
    "GUST": 0x10, "WING ATTACK": 0x11, "WHIRLWIND": 0x12, "FLY": 0x13, "BIND": 0x14,
    "SLAM": 0x15, "VINE WHIP": 0x16, "STOMP": 0x17, "DOUBLE KICK": 0x18, "MEGA KICK": 0x19,
    "JUMP KICK": 0x1A, "ROLLING KICK": 0x1B, "SAND-ATTACK": 0x1C, "HEADBUTT": 0x1D, "HORN ATTACK": 0x1E,
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
    "DIG": 0x5B, "TOXIC": 0x5C, "PSYCHIC": 0x5D, "HYPNOSIS": 0x5E, "MEDITATE": 0x5F,
    "AGILITY": 0x60, "QUICK ATTACK": 0x61, "RAGE": 0x62, "TELEPORT": 0x63, "NIGHT SHADE": 0x64,
    "MIMIC": 0x65, "SCREECH": 0x66, "DOUBLE TEAM": 0x67, "RECOVER": 0x68, "HARDEN": 0x69,
    "MINIMIZE": 0x6A, "SMOKESCREEN": 0x6B, "CONFUSE RAY": 0x6C, "WITHDRAW": 0x6D, "DEFENSE CURL": 0x6E,
    "BARRIER": 0x6F, "LIGHT SCREEN": 0x70, "HAZE": 0x71, "REFLECT": 0x72, "FOCUS ENERGY": 0x73,
    "BIDE": 0x74, "METRONOME": 0x75, "MIRROR MOVE": 0x76, "SELFDESTRUCT": 0x77, "EGG BOMB": 0x78,
    "LICK": 0x79, "SMOG": 0x7A, "SLUDGE": 0x7B, "BONE CLUB": 0x7C, "FIRE BLAST": 0x7D,
    "WATERFALL": 0x7E, "CLAMP": 0x7F, "SWIFT": 0x80, "SKULL BASH": 0x81, "SOFTBOILED": 0x86,
    "DREAM EATER": 0x89, "EXPLOSION": 0x98, "ROCK SLIDE": 0x9C, "TRI ATTACK": 0xA0, "SLASH": 0xA2,
    "SUBSTITUTE": 0xA3, "STRUGGLE": 0xA4
}

MOVES_INFO = {
    0x01: {"name": "POUND", "type": 0x00},
    0x02: {"name": "KARATE CHOP", "type": 0x00},
    0x03: {"name": "DOUBLESLAP", "type": 0x00},
    0x04: {"name": "COMET PUNCH", "type": 0x00},
    0x05: {"name": "MEGA PUNCH", "type": 0x00},
    0x06: {"name": "PAY DAY", "type": 0x00},
    0x07: {"name": "FIRE PUNCH", "type": 0x14},
    0x08: {"name": "ICE PUNCH", "type": 0x19},
    0x09: {"name": "THUNDERPUNCH", "type": 0x17},
    0x0A: {"name": "SCRATCH", "type": 0x00},
    0x0B: {"name": "VICEGRIP", "type": 0x00},
    0x0C: {"name": "GUILLOTINE", "type": 0x00},
    0x0D: {"name": "RAZOR WIND", "type": 0x00},
    0x0E: {"name": "SWORDS DANCE", "type": 0x00},
    0x0F: {"name": "CUT", "type": 0x00},
    0x10: {"name": "GUST", "type": 0x00},
    0x11: {"name": "WING ATTACK", "type": 0x02},
    0x12: {"name": "WHIRLWIND", "type": 0x00},
    0x13: {"name": "FLY", "type": 0x02},
    0x14: {"name": "BIND", "type": 0x00},
    0x15: {"name": "SLAM", "type": 0x00},
    0x16: {"name": "VINE WHIP", "type": 0x16},
    0x17: {"name": "STOMP", "type": 0x00},
    0x18: {"name": "DOUBLE KICK", "type": 0x01},
    0x19: {"name": "MEGA KICK", "type": 0x00},
    0x1A: {"name": "JUMP KICK", "type": 0x01},
    0x1B: {"name": "ROLLING KICK", "type": 0x01},
    0x1C: {"name": "SAND-ATTACK", "type": 0x00},
    0x1D: {"name": "HEADBUTT", "type": 0x00},
    0x1E: {"name": "HORN ATTACK", "type": 0x00},
    0x1F: {"name": "FURY ATTACK", "type": 0x00},
    0x20: {"name": "HORN DRILL", "type": 0x00},
    0x21: {"name": "TACKLE", "type": 0x00},
    0x22: {"name": "BODY SLAM", "type": 0x00},
    0x23: {"name": "WRAP", "type": 0x00},
    0x24: {"name": "TAKE DOWN", "type": 0x00},
    0x25: {"name": "THRASH", "type": 0x00},
    0x26: {"name": "DOUBLE-EDGE", "type": 0x00},
    0x27: {"name": "TAIL WHIP", "type": 0x00},
    0x28: {"name": "POISON STING", "type": 0x03},
    0x29: {"name": "TWINEEDLE", "type": 0x07},
    0x2A: {"name": "PIN MISSILE", "type": 0x07},
    0x2B: {"name": "LEER", "type": 0x00},
    0x2C: {"name": "BITE", "type": 0x00},
    0x2D: {"name": "GROWL", "type": 0x00},
    0x2E: {"name": "ROAR", "type": 0x00},
    0x2F: {"name": "SING", "type": 0x00},
    0x30: {"name": "SUPERSONIC", "type": 0x00},
    0x31: {"name": "SONICBOOM", "type": 0x00},
    0x32: {"name": "DISABLE", "type": 0x00},
    0x33: {"name": "ACID", "type": 0x03},
    0x34: {"name": "EMBER", "type": 0x14},
    0x35: {"name": "FLAMETHROWER", "type": 0x14},
    0x36: {"name": "MIST", "type": 0x19},
    0x37: {"name": "WATER GUN", "type": 0x15},
    0x38: {"name": "HYDRO PUMP", "type": 0x15},
    0x39: {"name": "SURF", "type": 0x15},
    0x3A: {"name": "ICE BEAM", "type": 0x19},
    0x3B: {"name": "BLIZZARD", "type": 0x19},
    0x3C: {"name": "PSYBEAM", "type": 0x18},
    0x3D: {"name": "BUBBLEBEAM", "type": 0x15},
    0x3E: {"name": "AURORA BEAM", "type": 0x19},
    0x3F: {"name": "HYPER BEAM", "type": 0x00},
    0x40: {"name": "PECK", "type": 0x02},
    0x41: {"name": "DRILL PECK", "type": 0x02},
    0x42: {"name": "SUBMISSION", "type": 0x01},
    0x43: {"name": "LOW KICK", "type": 0x01},
    0x44: {"name": "COUNTER", "type": 0x01},
    0x45: {"name": "SEISMIC TOSS", "type": 0x01},
    0x46: {"name": "STRENGTH", "type": 0x00},
    0x47: {"name": "ABSORB", "type": 0x16},
    0x48: {"name": "MEGA DRAIN", "type": 0x16},
    0x49: {"name": "LEECH SEED", "type": 0x16},
    0x4A: {"name": "GROWTH", "type": 0x00},
    0x4B: {"name": "RAZOR LEAF", "type": 0x16},
    0x4C: {"name": "SOLARBEAM", "type": 0x16},
    0x4D: {"name": "POISONPOWDER", "type": 0x03},
    0x4E: {"name": "STUN SPORE", "type": 0x16},
    0x4F: {"name": "SLEEP POWDER", "type": 0x16},
    0x50: {"name": "PETAL DANCE", "type": 0x16},
    0x51: {"name": "STRING SHOT", "type": 0x07},
    0x52: {"name": "DRAGON RAGE", "type": 0x1A},
    0x53: {"name": "FIRE SPIN", "type": 0x14},
    0x54: {"name": "THUNDERSHOCK", "type": 0x17},
    0x55: {"name": "THUNDERBOLT", "type": 0x17},
    0x56: {"name": "THUNDER WAVE", "type": 0x17},
    0x57: {"name": "THUNDER", "type": 0x17},
    0x58: {"name": "ROCK THROW", "type": 0x05},
    0x59: {"name": "EARTHQUAKE", "type": 0x04},
    0x5A: {"name": "FISSURE", "type": 0x04},
    0x5B: {"name": "DIG", "type": 0x04},
    0x5C: {"name": "TOXIC", "type": 0x03},
    0x5D: {"name": "PSYCHIC", "type": 0x18},
    0x5E: {"name": "HYPNOSIS", "type": 0x18},
    0x5F: {"name": "MEDITATE", "type": 0x18},
    0x60: {"name": "AGILITY", "type": 0x18},
    0x61: {"name": "QUICK ATTACK", "type": 0x00},
    0x62: {"name": "RAGE", "type": 0x00},
    0x63: {"name": "TELEPORT", "type": 0x18},
    0x64: {"name": "NIGHT SHADE", "type": 0x08},
    0x65: {"name": "MIMIC", "type": 0x00},
    0x66: {"name": "SCREECH", "type": 0x00},
    0x67: {"name": "DOUBLE TEAM", "type": 0x00},
    0x68: {"name": "RECOVER", "type": 0x00},
    0x69: {"name": "HARDEN", "type": 0x00},
    0x6A: {"name": "MINIMIZE", "type": 0x00},
    0x6B: {"name": "SMOKESCREEN", "type": 0x00},
    0x6C: {"name": "CONFUSE RAY", "type": 0x08},
    0x6D: {"name": "WITHDRAW", "type": 0x15},
    0x6E: {"name": "DEFENSE CURL", "type": 0x00},
    0x6F: {"name": "BARRIER", "type": 0x18},
    0x70: {"name": "LIGHT SCREEN", "type": 0x18},
    0x71: {"name": "HAZE", "type": 0x19},
    0x72: {"name": "REFLECT", "type": 0x18},
    0x73: {"name": "FOCUS ENERGY", "type": 0x00},
    0x74: {"name": "BIDE", "type": 0x00},
    0x75: {"name": "METRONOME", "type": 0x00},
    0x76: {"name": "MIRROR MOVE", "type": 0x02},
    0x77: {"name": "SELFDESTRUCT", "type": 0x00},
    0x78: {"name": "EGG BOMB", "type": 0x00},
    0x79: {"name": "LICK", "type": 0x08},
    0x7A: {"name": "SMOG", "type": 0x03},
    0x7B: {"name": "SLUDGE", "type": 0x03},
    0x7C: {"name": "BONE CLUB", "type": 0x04},
    0x7D: {"name": "FIRE BLAST", "type": 0x14},
    0x7E: {"name": "WATERFALL", "type": 0x15},
    0x7F: {"name": "CLAMP", "type": 0x15},
    0x80: {"name": "SWIFT", "type": 0x00},
    0x81: {"name": "SKULL BASH", "type": 0x00},
    0x86: {"name": "SOFTBOILED", "type": 0x00},
    0x89: {"name": "DREAM EATER", "type": 0x18},
    0x98: {"name": "EXPLOSION", "type": 0x00},
    0x9C: {"name": "ROCK SLIDE", "type": 0x05},
    0xA0: {"name": "TRI ATTACK", "type": 0x00},
    0xA2: {"name": "SLASH", "type": 0x00},
    0xA3: {"name": "SUBSTITUTE", "type": 0x00},
    0xA4: {"name": "STRUGGLE", "type": 0x00}
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
