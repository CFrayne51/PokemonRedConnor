
# Memory Addresses
EVENT_FLAGS_START = 0xD747
EVENT_FLAGS_END = 0xD87E
MUSEUM_TICKET = (0xD754, 0)

# HP Addresses
HP_ADDRS = [0xD16C, 0xD198, 0xD1C4, 0xD1F0, 0xD21C, 0xD248]
MAX_HP_ADDRS = [0xD18D, 0xD1B9, 0xD1E5, 0xD211, 0xD23D, 0xD269]

# Enemy HP Addresses
ENEMY_HP_ADDRS = [0xD8A5, 0xD8D1, 0xD8FD, 0xD929, 0xD955, 0xD981]
ENEMY_MAX_HP_ADDRS = [0xD8C6, 0xD8F2, 0xD91E, 0xD94A, 0xD976, 0xD9A2]
ENEMY_PARTY_COUNT = 0xD89C

# Party Info
PARTY_SIZE_ADDR = 0xD163
PARTY_LEVEL_ADDRS = [0xD18C, 0xD1B8, 0xD1E4, 0xD210, 0xD23C, 0xD268]
PARTY_TYPE_ADDRS = [0xD164, 0xD165, 0xD166, 0xD167, 0xD168, 0xD169]

# Location / Map
X_POS_ADDR = 0xD362
Y_POS_ADDR = 0xD361
MAP_N_ADDR = 0xD35E
BADGE_COUNT_ADDR = 0xD356

# Battle
IN_BATTLE_FLAG = 0xD057
OPPONENT_LEVEL_ADDRS = [0xD8C5, 0xD8F1, 0xD91D, 0xD949, 0xD975, 0xD9A1]

# Essential Map Locations for progress tracking
ESSENTIAL_MAP_LOCATIONS = {
    v: i for i, v in enumerate([
        40, 0, 12, 1, 13, 51, 2, 54, 14, 59, 60, 61, 15, 3, 65
    ])
}

# Config Defaults
DEFAULT_CONFIG = {
    "headless": True,
    "save_final_state": False,
    "early_stop": False,
    "action_freq": 24,
    "init_state": "init.state",
    "max_steps": 2048*10,
    "print_rewards": False,
    "save_video": False,
    "fast_video": True,
    "session_path": "sessions",
    "gb_path": "./PokemonRed.gb",
    "debug": False,
    "sim_frame_dist": 2000000.0,
    "extra_buttons": False,
    "explore_weight": 1,
    "reward_scale": 1,
}
