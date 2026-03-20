import sys
from os.path import exists
from pathlib import Path
from red_gym.environment import RedGymEnv
from stable_baselines3 import PPO
from stable_baselines3.common import env_checker
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.common.utils import set_random_seed
from stable_baselines3.common.callbacks import CheckpointCallback, CallbackList
from tensorboard_callback import TensorboardCallback
from aggregated_logger import GlobalEpisodeLogger
import json
import glob
from datetime import datetime
import numpy as np
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import BaseCallback

class BattleEvalCallback(BaseCallback):
    def __init__(self, eval_freq, test_state_dir, log_dir, env_config, n_random=5, verbose=0):
        super().__init__(verbose)
        self.eval_freq = eval_freq
        self.test_state_dir = test_state_dir
        self.log_dir = log_dir
        self.env_config = env_config
        self.n_random = n_random
        self.iteration_count = 0
        self.log_file = Path(log_dir) / "test_winrates.jsonl"
        
        # Robust pathing: check v2/ prefix then relative
        self.test_states = sorted(glob.glob(str(Path(test_state_dir) / "*.state")))
        if not self.test_states and not test_state_dir.startswith("v2/"):
            alt_path = Path("v2") / test_state_dir
            self.test_states = sorted(glob.glob(str(alt_path / "*.state")))
            
        # Resume iteration count if log exists
        if self.log_file.exists():
            try:
                with open(self.log_file, "r") as f:
                    lines = f.readlines()
                    if lines:
                        last_entry = json.loads(lines[-1].strip())
                        self.iteration_count = last_entry.get("iteration", 0)
                        if self.verbose > 0:
                            print(f"[EVAL] Resuming from iteration {self.iteration_count} based on log file.")
            except Exception as e:
                if self.verbose > 0:
                    print(f"[EVAL] Could not read previous iteration from log: {e}")
            
        if self.verbose > 0:
            print(f"[EVAL] Initialized with {len(self.test_states)} test states.")

    def _run_eval_on_states(self, model, env_config, states, deterministic=True):
        wins = []
        action_counts = {}
        for state in states:
            action_counts = {}
            conf = env_config.copy()
            conf.update({
                'init_state': state, 
                'headless': True, 
                'save_video': False, 
                'print_rewards': False
            })
            
            # Wrap in DummyVecEnv for perfect consistency with training
            eval_env = DummyVecEnv([lambda: RedGymEnv(conf)])
            obs = eval_env.reset()
            done = [False]
            total_reward = 0
            steps = 0
            
            won_episode = False
            while not done[0]:
                # Using deterministic=False as per user manual test success
                action, _ = model.predict(obs, deterministic=False)
                
                # Track actions for debugging
                act_val = int(action[0])
                action_counts[act_val] = action_counts.get(act_val, 0) + 1
                
                obs, rewards, dones, infos = eval_env.step(action)
                
                info = infos[0]
                if info.get("win", False) or info.get("won", 0) == 1:
                    won_episode = True
                if info.get("terminal_info", {}).get("win", False) or info.get("terminal_info", {}).get("won", 0) == 1:
                    won_episode = True

                done = dones
                total_reward += rewards[0]
                steps += 1
            
            # Robust win logic: check env flags OR if we ended with positive reward
            won = 1 if (won_episode or total_reward > 0) else 0
            wins.append(won)
            
            if self.verbose > 0:
                print(f"[EVAL] State: {Path(state).name} | Steps: {steps} | Reward: {total_reward:.2f} | Result: {'WIN' if won else 'LOSS'} | Actions: {action_counts}")
            
            eval_env.close()
            
        if self.verbose > 0:
            print(f"[EVAL] Action distribution: {action_counts}")
        return np.mean(wins) if wins else 0

    def _on_rollout_start(self) -> None:
        self.iteration_count += 1
        if self.iteration_count % self.eval_freq == 0:
            if self.verbose > 0: print(f"\n[EVAL] Iteration {self.iteration_count}: Running evaluation...")
            
            # 1. Test states (fixed)
            test_wr = self._run_eval_on_states(self.model, self.env_config, self.test_states)
            
            # 2. Training states (randomized)
            random_wins = []
            for i in range(self.n_random):
                conf = self.env_config.copy()
                conf.update({
                    'randomize_pokemon': False, 
                    'headless': True, 
                    'save_video': False, 
                    'print_rewards': False
                })
                if 'init_state' in conf: del conf['init_state']
                
                eval_env = DummyVecEnv([lambda: RedGymEnv(conf)])
                obs = eval_env.reset()
                done = [False]
                total_reward = 0
                won_episode = False
                while not done[0]:
                    # Using deterministic=False as per user manual test success
                    action, _ = self.model.predict(obs, deterministic=False)
                    obs, rewards, dones, infos = eval_env.step(action)
                    
                    info = infos[0]
                    if info.get("win", False) or info.get("won", 0) == 1:
                        won_episode = True
                    if info.get("terminal_info", {}).get("win", False) or info.get("terminal_info", {}).get("won", 0) == 1:
                        won_episode = True
                        
                    done = dones
                    total_reward += rewards[0]
                
                # Robust win logic: check env flags OR if we ended with positive reward
                won = 1 if (won_episode or total_reward > 0) else 0
                random_wins.append(won)
                eval_env.close()
                if self.verbose > 0: print(f"[EVAL] Random episode {i+1}/{self.n_random} result: {'WIN' if won else 'LOSS'}")
                
            train_wr = np.mean(random_wins) if random_wins else 0

            # Log results
            self.logger.record("eval/test_winrate", test_wr)
            self.logger.record("eval/train_winrate", train_wr)
            entry = {"iteration": self.iteration_count, "timestamp": datetime.now().isoformat(), "test_winrate": float(test_wr), "train_winrate": float(train_wr)}
            with open(self.log_file, "a") as f: f.write(json.dumps(entry) + "\n")
            if self.verbose > 0: print(f"[EVAL] Summary - Test WR: {test_wr:.4f}, Train WR: {train_wr:.4f}\n")

    def _on_step(self) -> bool: return True


def make_env(rank, env_conf, seed=0):
    """
    Utility function for multiprocessed env.
    :param env_id: (str) the environment ID
    :param num_env: (int) the number of environments you wish to have in subprocesses
    :param seed: (int) the initial seed for RNG
    :param rank: (int) index of the subprocess
    """
    def _init():
        import gymnasium as gym
        env = RedGymEnv(env_conf)
        env = gym.wrappers.RecordEpisodeStatistics(env)
        env.reset(seed=(seed + rank))
        return env
    set_random_seed(seed)
    return _init

if __name__ == "__main__":

    use_wandb_logging = False
    ep_length = 8192
    sess_id = "battle_runs"
    sess_path = Path(sess_id)

    env_config = {
                'headless': True, 'save_final_state': False, 'early_stop': True,
                'action_freq': 60, 'max_steps': ep_length, 
                'print_rewards': True, 'save_video': True, 'fast_video': True, 'session_path': sess_path,
                'gb_path': 'PokemonRed.gb', 'debug': True, 'reward_scale': 0.5, 'explore_weight': 0.25,
                'randomize_pokemon': False
            }
    
    print(env_config)
    
    num_cpu = 16 # Also sets the number of episodes per training iteration
    
    # Quick Smoke Test if debug is on
    if env_config.get("debug", False):
        print("\n[DEBUG] Running modular environment smoke test...")
        test_env = make_env(0, env_config)()
        # Reset to get obs
        obs, info = test_env.reset()
        print(f"[DEBUG] Smoke test starting state: {getattr(test_env.unwrapped, 'last_state_path', 'unknown')}")
        print(f"[DEBUG] Smoke test observation keys: {obs.keys()}")
        print(f"[DEBUG] Move IDs from RAM: {obs['move_ids']}")
        
        # Run a few steps to get a reward
        total_reward = 0
        for _ in range(5):
            obs, reward, terminated, truncated, info = test_env.step(test_env.action_space.sample())
            total_reward += reward
        
        print(f"[DEBUG] Smoke test total reward (5 steps): {total_reward}")
        test_env.close()
        print("[DEBUG] Smoke test complete.\n")

    env = SubprocVecEnv([make_env(i, env_config) for i in range(num_cpu)])
    
    checkpoint_callback = CheckpointCallback(save_freq=ep_length//2, save_path="runs", name_prefix="poke")
    
    callbacks = [checkpoint_callback, TensorboardCallback(sess_path)]

    if use_wandb_logging:
        import wandb
        from wandb.integration.sb3 import WandbCallback
        wandb.tensorboard.patch(root_logdir=str(sess_path))
        run = wandb.init(
            project="pokemon-train",
            id=sess_id,
            name="v2-a",
            config=env_config,
            sync_tensorboard=True,  
            monitor_gym=True,  
            save_code=True,
        )
        callbacks.append(WandbCallback())

    #env_checker.check_env(env)

    # put a checkpoint here you want to start from    
    if sys.stdin.isatty():
        file_name = ""
    else:
        file_name = sys.stdin.read().strip() #"runs/poke_26214400_steps"

    train_steps_batch = ep_length // 64
    
    if exists(file_name + ".zip"):
        print("\nloading checkpoint")
        model = PPO.load(file_name, env=env)
        model.n_steps = train_steps_batch
        model.n_envs = num_cpu
        model.rollout_buffer.buffer_size = train_steps_batch
        model.rollout_buffer.n_envs = num_cpu
        model.rollout_buffer.reset()
    else:
        model = PPO("MultiInputPolicy", env, verbose=1, n_steps=train_steps_batch, batch_size=512, n_epochs=1, gamma=0.997, ent_coef=0.01, tensorboard_log=sess_path)
    
    print(model.policy)

    global_logger = GlobalEpisodeLogger(num_envs=num_cpu, save_path=sess_path)
    eval_env_conf = env_config.copy()
    eval_env_conf['max_steps'] = 16000 # Give it more room to finish battles
    eval_callback = BattleEvalCallback(
        eval_freq=500, 
        test_state_dir="v2/battle_states/Test", 
        log_dir=sess_path,
        env_config=eval_env_conf,
        n_random=20,
        verbose=1
    )
    callbacks = [checkpoint_callback, TensorboardCallback(sess_path), global_logger, eval_callback]

    model.learn(total_timesteps=(ep_length)*num_cpu*10000, callback=CallbackList(callbacks), tb_log_name="poke_ppo")

    if use_wandb_logging:
        run.finish()
