
import uuid
import json
import random
import numpy as np
import atexit
from pathlib import Path
from datetime import datetime

import mediapy as media
from skimage.transform import downscale_local_mean
from gymnasium import Env, spaces
from pyboy import PyBoy
from pyboy.utils import WindowEvent
import os

from .constants import (
    DEFAULT_CONFIG, ESSENTIAL_MAP_LOCATIONS, 
    EVENT_FLAGS_START, EVENT_FLAGS_END, IN_BATTLE_FLAG
)
from .memory import PyBoyMemory
from .rewards import RewardSystem
from .ocr import GameParser
from .pokemon_data import MOVES_MAP

class RedGymEnv(Env):
    def __init__(self, config=None):
        self.config = DEFAULT_CONFIG.copy()
        if config:
            self.config.update(config)

        self.headless = self.config["headless"]
        self.action_freq = self.config["action_freq"]
        self.max_steps = self.config["max_steps"]
        self.save_video = self.config["save_video"]
        self.fast_video = self.config["fast_video"]
        self.randomize_pokemon = self.config.get("randomize_pokemon", True)
        self.frame_stacks = 3
        
        # Unique instance ID if not provided in config
        if "instance_id" not in self.config:
            self.instance_id = str(uuid.uuid4())[:8]

        # Handle State Directory
        self.state_dir = Path(self.config.get("state_dir", "v2/battle_states"))
        self.all_states = [str(s) for s in self.state_dir.glob("*.state")]
        if not self.all_states:
             # Fallback to single state if dir is empty/missing
             base_state = self.config["gb_path"] + ".state"
             if os.path.exists(base_state):
                 self.all_states = [base_state]

        self.pyboy = None
        self._init_pyboy()

        self.s_path = Path(self.config["session_path"])
        self.s_path.mkdir(exist_ok=True, parents=True)
            
        # Video writers
        self.full_frame_writer = None
        self.reset_count = 0
        self.step_count = 0
        
        self.memory = PyBoyMemory(self.pyboy)
        self.reward_system = RewardSystem(self.memory, self.config)
        self.parser = GameParser(self.s_path)
        
        atexit.register(self.close)
        
        # Actions
        self.valid_actions = [
            WindowEvent.PRESS_ARROW_DOWN,
            WindowEvent.PRESS_ARROW_LEFT,
            WindowEvent.PRESS_ARROW_RIGHT,
            WindowEvent.PRESS_ARROW_UP,
            WindowEvent.PRESS_BUTTON_A,
            WindowEvent.PRESS_BUTTON_B,
            WindowEvent.PRESS_BUTTON_START,
        ]

        self.release_actions = [
            WindowEvent.RELEASE_ARROW_DOWN,
            WindowEvent.RELEASE_ARROW_LEFT,
            WindowEvent.RELEASE_ARROW_RIGHT,
            WindowEvent.RELEASE_ARROW_UP,
            WindowEvent.RELEASE_BUTTON_A,
            WindowEvent.RELEASE_BUTTON_B,
            WindowEvent.RELEASE_BUTTON_START
        ]

        self.action_space = spaces.Discrete(len(self.valid_actions))
        
        # Observations
        self.output_shape = (72, 80, self.frame_stacks)
        self.enc_freqs = 8
        
        # DUMMY MAP for compatibility
        # Original shape: (self.coords_pad*4, self.coords_pad*4, 1) -> (48, 48, 1)
        self.dummy_map = np.zeros((48, 48, 1), dtype=np.uint8)

        self.observation_space = spaces.Dict(
            {
                "screens": spaces.Box(low=0, high=255, shape=self.output_shape, dtype=np.uint8),
                "health": spaces.Box(low=0, high=1, shape=(1,)),
                "level": spaces.Box(low=-1, high=1, shape=(self.enc_freqs,)),
                "recent_actions": spaces.MultiDiscrete([len(self.valid_actions)] * self.frame_stacks),
                "move_ids": spaces.Box(low=0, high=255, shape=(4,), dtype=np.int32)
            }
        )

        self.recent_screens = np.zeros(self.output_shape, dtype=np.uint8)
        self.recent_actions = np.zeros((self.frame_stacks,), dtype=np.uint8)


    def _init_pyboy(self):
        head = "null" if self.headless else "SDL2"
        self.pyboy = PyBoy(
            self.config["gb_path"],
            window=head,
        )
        self.pyboy.set_emulation_speed(0 if self.headless else 6)

    def reset(self, seed=None, options={}):
        self.seed = seed
        
        # Load State - Pick random state from the battle_states folder
        if self.all_states:
            state_path = self.np_random.choice(self.all_states)
        else:
            state_path = self.config["gb_path"] + ".state"
            
        with open(state_path, "rb") as f:
            self.pyboy.load_state(f)
        
        if self.randomize_pokemon:
            if self.config.get("debug", False):
                print(f"[DEBUG][{self.instance_id}] Injecting RAM for reset {self.reset_count}")
            self.memory.inject_ram()
            
            # Wait loop to let the battle transition occur naturally
            # and let RAM injection "settle"
            self._wait_for_battle()
            
            if self.config.get("debug", False):
                hp = self.memory.read_hp_fraction()
                ehp = self.memory.read_enemy_hp_fraction()
                print(f"[DEBUG][{self.instance_id}] HP: {hp:.2f}, E-HP: {ehp:.2f}")

        self.reward_system.reset()
        self.step_count = 0
        self.reset_count += 1
        
        # Reset buffers
        self.recent_screens = np.zeros(self.output_shape, dtype=np.uint8)
        self.recent_actions = np.zeros((self.frame_stacks,), dtype=np.uint8)
        
        self.update_recent_screens(self.render())

        return self._get_obs(), {}

    def step(self, action):
        if self.save_video and self.step_count == 0:
            self.start_video()
            
        self._run_action(action)
        self._update_recent_actions(action)
        
        # Update Screen Buffer
        self.update_recent_screens(self.render())
        
        request_reward = self.reward_system.update_reward(self.step_count, self.max_steps)
        
        terminated = False
        truncated = False
        
        if self.check_if_done():
             # Basic check, refine logic
             terminated = True 

        # Timeout check
        if self.step_count >= self.max_steps - 1:
            truncated = True

        info = {
            "stats": self.reward_system.progress_reward,
            "win": False,
            "loss": False,
            "hp": self.memory.read_hp_fraction(),
            "enemy_hp": self.memory.read_enemy_hp_fraction()
        }
        
        if terminated or truncated:
            if info["enemy_hp"] <= 0:
                info["win"] = True
            elif info["hp"] <= 0:
                info["loss"] = True
            self.close_video()

        self.step_count += 1

        return self._get_obs(), request_reward, terminated, truncated, info

    def _update_agent_stats(self):
        # Update explore map (basic downscale)
        x, y, map_n = self.memory.get_pos()
        if map_n in ESSENTIAL_MAP_LOCATIONS:
             self.explore_map[y//4, x//4] = 1 
        
        # Pull stats from reward system
        self.agent_stats.append(self.reward_system.progress_reward.copy())
        self.agent_stats[-1].update({
            "step": self.step_count,
            "reset": self.reset_count,
            "hp": self.memory.read_hp_fraction(),
            "enemy_hp": self.memory.read_enemy_hp_fraction()
        })

    def _run_action(self, action_idx):
        if self.save_video and self.fast_video:
             self.add_video_frame()
             
        self.pyboy.send_input(self.valid_actions[action_idx])
        
        # Hold for some frames? Original was:
        # press_step = 8
        # wait total act_freq
        press_step = 8
        self.pyboy.tick(press_step, False) # Render false mainly?
        self.pyboy.send_input(self.release_actions[action_idx])
        self.pyboy.tick(self.action_freq - press_step - 1, False)
        self.pyboy.tick(1, True) # Render frame
        
    def render(self, reduce_res=True):
        game_pixels_render = self.pyboy.screen.ndarray[:,:,0:1]  # (144, 160, 1)
        if reduce_res:
            game_pixels_render = (
                downscale_local_mean(game_pixels_render, (2,2,1))
            ).astype(np.uint8)
        return game_pixels_render

    def _get_obs(self):
        # Stub level encoding
        level_sum = 0 # Implement real logic if needed
        
        return {
            "screens": self.recent_screens,
            "health": np.array([self.memory.read_hp_fraction()]),
            "level": self.fourier_encode(level_sum),
            "recent_actions": self.recent_actions,
            "move_ids": np.array(self.memory.read_moves(), dtype=np.int32)
        }

    def update_recent_screens(self, cur_screen):
        self.recent_screens = np.roll(self.recent_screens, 1, axis=2)
        self.recent_screens[:, :, 0] = cur_screen[:,:, 0]

    def _update_recent_actions(self, action):
        self.recent_actions = np.roll(self.recent_actions, 1)
        self.recent_actions[0] = action

    def fourier_encode(self, val):
        return np.sin(val * 2 ** np.arange(self.enc_freqs))

    def check_if_done(self):
        # 1. Timeout
        if self.step_count >= self.max_steps - 1:
            if self.config.get("debug", False): print(f"[DEBUG][{self.instance_id}] Done: Timeout ({self.step_count})")
            return True
        
        # 2. Battle finished (Enemy fainted or We fainted)
        # Note: read_hp_fraction reads the sum of the WHOLE party HP
        ehp = self.memory.read_enemy_hp_fraction()
        php = self.memory.read_hp_fraction()
        
        if ehp <= 0.0:
            if self.config.get("debug", False): print(f"[DEBUG][{self.instance_id}] Done: Enemy Fainted (E-HP: {ehp})")
            return True
        if php <= 0.0:
            if self.config.get("debug", False): print(f"[DEBUG][{self.instance_id}] Done: Player Fainted (P-HP: {php})")
            return True

        # 3. Not in battle anymore check (after initial delay)
        # If the active pokemon faints and we are prompted to switch, we might still be "in battle"
        # but if the battle ends (e.g. run away or last mon faints), IN_BATTLE_FLAG goes to 0
        if self.step_count > 100:
             if self.memory.read_m(0xD057) == 0: # IN_BATTLE_FLAG
                 if self.config.get("debug", False): print(f"[DEBUG][{self.instance_id}] Done: Out of Battle (Flag 0)")
                 return True
                 
        return False

    def start_video(self):
        base_dir = self.s_path / Path("rollouts")
        base_dir.mkdir(exist_ok=True)
        full_name = Path(f"full_reset_{self.reset_count}_id{self.instance_id}").with_suffix(".mp4")
        self.full_frame_writer = media.VideoWriter(
            base_dir / full_name, (144, 160), fps=60, input_format="gray"
        )
        self.full_frame_writer.__enter__()

    def add_video_frame(self):
        if self.full_frame_writer:
            self.full_frame_writer.add_image(self.render(reduce_res=False)[:,:,0])

    def close_video(self):
        if self.full_frame_writer:
            self.full_frame_writer.close()
            self.full_frame_writer = None

    def _wait_for_battle(self):
        # We wait for the battle flag to be set
        # Max wait of ~10 seconds (600 frames)
        max_wait = 600
        for i in range(max_wait):
            self.pyboy.tick(1, True)
            if self.memory.read_m(0xD057) > 0: # IN_BATTLE_FLAG
                if self.config.get("debug", False):
                    print(f"[DEBUG][{self.instance_id}] Battle detected at tick {i}")
                break
        else:
            if self.config.get("debug", False):
                print(f"[DEBUG][{self.instance_id}] Warning: Battle flag not set after {max_wait} ticks")

    def close(self):
        self.close_video()
        if self.pyboy:
            self.pyboy.stop()
