from stable_baselines3.common.vec_env import DummyVecEnv
from red_gym.environment import RedGymEnv
import os
import glob
from stable_baselines3 import PPO
from pathlib import Path
import numpy as np

conf = {
    'headless': True, 
    'save_video': False, 
    'print_rewards': False,
    'randomize_pokemon': False,
    'session_path': 'C:/Users/conno/Documents/PokemonRedConnor/v2/test_debug',
    'gb_path': 'C:/Users/conno/Documents/PokemonRedConnor/PokemonRed.gb',
    'action_freq': 60,
    'max_steps': 500,
    'state_dir': 'C:/Users/conno/Documents/PokemonRedConnor/v2/battle_states'
}

ckpts = glob.glob('C:/Users/conno/Documents/PokemonRedConnor/v2/runs/*.zip')
if not ckpts:
    print("No checkpoints found. Testing with a random-action agent.")
    class DummyModel:
        def predict(self, obs, deterministic=True):
            return [0], None
    model = DummyModel()
else:
    print(f"Loading checkpoint {ckpts[-1]}")
    model = PPO.load(ckpts[-1], custom_objects={"lr_schedule": 0, "clip_range": 0})

print("Starting 5 train_winrate evaluations...")
random_wins = []
for i in range(5):
    eval_env = DummyVecEnv([lambda: RedGymEnv(conf)])
    obs = eval_env.reset()
    done = [False]
    total_reward = 0
    won_episode = False
    steps = 0
    while not done[0] and steps < 800:
        action, _ = model.predict(obs, deterministic=True)
        obs, rewards, dones, infos = eval_env.step(action)
        
        info = infos[0]
        if info.get("win", False) or info.get("won", 0) == 1:
            won_episode = True
        if info.get("terminal_info", {}).get("win", False) or info.get("terminal_info", {}).get("won", 0) == 1:
            won_episode = True
            
        done = dones
        total_reward += rewards[0]
        steps += 1
    
    won = 1 if won_episode else 0
    random_wins.append(won)
    print(f"Eval {i} -> Won: {won_episode}, Steps: {steps}")
    eval_env.close()

print("Train Winrate:", np.mean(random_wins))
