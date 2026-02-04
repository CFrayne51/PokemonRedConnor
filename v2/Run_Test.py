from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from pathlib import Path
import glob
import os

from red_gym_env_v2 import RedGymEnv
from ocr_wrapper import PokemonOCRWrapper


def get_latest_checkpoint(folder: str):
    files = glob.glob(os.path.join(folder, "*.zip"))
    return max(files, key=os.path.getmtime) if files else None

def get_earliest_checkpoint(folder: str):
    files = glob.glob(os.path.join(folder, "*.zip"))
    return min(files, key=os.path.getmtime) if files else None


if __name__ == "__main__":

    env_config = {
        "headless": False,
        "save_final_state": False,
        "early_stop": True,
        "action_freq": 60,
        "max_steps": 1000,
        "print_rewards": True,
        "save_video": True,
        "fast_video": False,
        "session_path": Path("battle_runs"),
        "gb_path": "/home/di-lab1/PokemonRedExperiments/PokemonRed.gb",
        "debug": False,
        "init_state": None,
        "randomize_pokemon": False
    }

    # 1 env, wrapped as VecEnv (what PPO expects)
    env = DummyVecEnv([lambda: PokemonOCRWrapper(RedGymEnv(env_config))])
    print("Env type:", type(env))

    
    #Loads specific
    ckpt = "runs/poke_383254528_steps.zip"
    #Loads lates checkpoint
    #ckpt = get_earliest_checkpoint("runs")
    if ckpt is None:
        raise RuntimeError("No checkpoint .zip files found in 'runs/'")
    print("Loading:", ckpt)

    model = PPO.load(ckpt, env=env, custom_objects={"lr_schedule": 0, "clip_range": 0})
    
    # Reset once, grab the real underlying env
    obs = env.reset()
    real_env: RedGymEnv = env.envs[0]

    # Start first episode's video
    real_env.start_video()
    print("Started video for first episode")

    try:
        while True:
            action, _ = model.predict(obs, deterministic=True)
            obs, rewards, dones, infos = env.step(action)

            # Write one frame per step
            real_env.add_video_frame()

            # If this episode finished, reset and start a new video
            if dones[0]:
                print("Episode ended → resetting + starting new video")
                obs = env.reset()
                real_env = env.envs[0]
                real_env.save_video = True
                real_env.fast_video = False
                real_env.start_video()

    except KeyboardInterrupt:
        print("KeyboardInterrupt → closing env")
    finally:
        env.close()
        print("[Run_Test] Closed env and video writers.")
