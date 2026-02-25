
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

from .constants import (
    DEFAULT_CONFIG, ESSENTIAL_MAP_LOCATIONS, 
    EVENT_FLAGS_START, EVENT_FLAGS_END, IN_BATTLE_FLAG
)
from .memory import PyBoyMemory
from .rewards import RewardSystem

class RedGymEnv(Env):
    def __init__(self, config=None):
        self.config = DEFAULT_CONFIG.copy()
        if config:
            self.config.update(config)

        self.s_path = Path(self.config["session_path"])
        self.s_path.mkdir(exist_ok=True, parents=True)
            
        self.headless = self.config["headless"]
        self.action_freq = self.config["action_freq"]
        self.max_steps = self.config["max_steps"]
        self.save_video = self.config["save_video"]
        self.fast_video = self.config["fast_video"]
        self.frame_stacks = 3
        
        self.instance_id = str(uuid.uuid4())[:8]
        
        # Video writers
        self.full_frame_writer = None
        
        self.reset_count = 0
        self.step_count = 0
        
        self._init_pyboy()
        self.memory = PyBoyMemory(self.pyboy)
        self.reward_system = RewardSystem(self.memory, self.config)
        
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
                "badges": spaces.MultiBinary(8),
                "events": spaces.MultiBinary((EVENT_FLAGS_END - EVENT_FLAGS_START) * 8),
                "map": spaces.Box(low=0, high=255, shape=(48, 48, 1), dtype=np.uint8),
                "recent_actions": spaces.MultiDiscrete([len(self.valid_actions)] * self.frame_stacks)
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
        
        # Load State
        if self.config["init_state"]:
             with open(self.config["init_state"], "rb") as f:
                self.pyboy.load_state(f)
        else:
            # Fallback for random testing
             pass

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
            "stats": self.reward_system.progress_reward
        }
        
        if terminated or truncated:
            self.close_video()

        self.step_count += 1
        return self._get_obs(), request_reward, terminated, truncated, info

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
            "badges": np.array([int(bit) for bit in f"{self.memory.read_m(0xD356):08b}"], dtype=np.int8),
            "events": np.zeros(((EVENT_FLAGS_END - EVENT_FLAGS_START) * 8,), dtype=np.int8), # Stub events for now or implement
            "map": self.dummy_map, 
            "recent_actions": self.recent_actions
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
            return True
        
        # 2. Battle finished (Enemy fainted or We fainted)
        if self.memory.read_enemy_hp_fraction() <= 0.0:
            return True
        if self.memory.read_hp_fraction() <= 0.0:
            return True

        # 3. Not in battle anymore check (after initial delay)
        if self.step_count > 60:
             if self.memory.read_m(IN_BATTLE_FLAG) == 0:
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

    def close(self):
        self.close_video()
        if self.pyboy:
            self.pyboy.stop()
