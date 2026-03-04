import sys
from os.path import exists
from pathlib import Path
from red_gym.environment import RedGymEnv
from stream_agent_wrapper import StreamWrapper
from stable_baselines3 import PPO
from stable_baselines3.common import env_checker
from stable_baselines3.common.vec_env import SubprocVecEnv
from stable_baselines3.common.utils import set_random_seed
from stable_baselines3.common.callbacks import CheckpointCallback, CallbackList
from tensorboard_callback import TensorboardCallback
from aggregated_logger import GlobalEpisodeLogger


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
        env = StreamWrapper(
            RedGymEnv(env_conf), 
            stream_metadata = { # All of this is part is optional
                "user": "v2-battle", # choose your own username
                "env_id": rank, # environment identifier
                "color": "#447799", # choose your color :)
                "extra": "", # any extra text you put here will be displayed
            }
        )
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
                'randomize_pokemon': True
            }
    
    print(env_config)
    
    num_cpu = 16 # Also sets the number of episodes per training iteration
    
    # Quick Smoke Test if debug is on
    if env_config.get("debug", False):
        print("\n[DEBUG] Running modular environment smoke test...")
        test_env = make_env(0, env_config)()
        # Reset to get obs
        obs, _ = test_env.reset()
        print(f"[DEBUG] Smoke test observation keys: {obs.keys()}")
        print(f"[DEBUG] Move IDs from RAM: {obs['move_ids']}")
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
    callbacks = [checkpoint_callback, TensorboardCallback(sess_path), global_logger]

    model.learn(total_timesteps=(ep_length)*num_cpu*10000, callback=CallbackList(callbacks), tb_log_name="poke_ppo")

    if use_wandb_logging:
        run.finish()
