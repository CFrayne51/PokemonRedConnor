import os
from stable_baselines3 import PPO
from pyboy import PyBoy
from pathlib import Path
import numpy as np

from v2Battle.red_gym.environment import RedGymEnv as BattleEnv
from v2.red_gym_env_v2 import RedGymEnv as OverworldEnv

def main():
    print("Loading models...")
    # Load trained battle model
    battle_model = PPO.load("runs/poke_72064000_steps.zip")
    
    # Load trained overworld model
    overworld_model = PPO.load("v2/runs/poke_26214400.zip")
    
    print("Initializing PyBoy...")
    pyboy = PyBoy("PokemonRed.gb", window="null")
    pyboy.set_emulation_speed(6)
    
    battle_config = {
        'headless': True, 'save_final_state': False, 'early_stop': False,
        'action_freq': 60, 'max_steps': 8192, 
        'print_rewards': False, 'save_video': False, 'fast_video': True, 
        'session_path': Path("hybrid_runs"), 'gb_path': 'PokemonRed.gb', 
        'debug': False, 'reward_scale': 0.5, 'explore_weight': 0.25,
        'randomize_pokemon': False
    }

    overworld_config = {
        'headless': True, 'save_final_state': False, 'early_stop': False,
        'action_freq': 24, 'init_state': 'v2/init.state', 'max_steps': 2048 * 80, 
        'print_rewards': False, 'save_video': False, 'fast_video': False, 
        'session_path': Path("hybrid_runs"), 'gb_path': 'PokemonRed.gb', 
        'debug': False, 'reward_scale': 0.5, 'explore_weight': 0.25
    }
    
    # Initialize observation generators using the external PyBoy made above
    battle_env = BattleEnv(config=battle_config, external_pyboy=pyboy)
    overworld_env = OverworldEnv(config=overworld_config, external_pyboy=pyboy)
    
    print("Initializing frame buffers without a hard game-reset...")
    # Because we skip calling 'env.reset()' (which would override PyBoy with a saved file), 
    # we must manually construct the memory arrays those functions normally create!
    from v2.global_map import GLOBAL_MAP_SHAPE
    
    battle_env.recent_screens = np.zeros(battle_env.output_shape, dtype=np.uint8)
    battle_env.recent_actions = np.zeros((battle_env.frame_stacks,), dtype=np.uint8)
    
    overworld_env.recent_screens = np.zeros(overworld_env.output_shape, dtype=np.uint8)
    overworld_env.recent_actions = np.zeros((overworld_env.frame_stacks,), dtype=np.uint8)
    overworld_env.explore_map = np.zeros(GLOBAL_MAP_SHAPE, dtype=np.uint8)
    
    print("Starting video recorder...")
    import mediapy as media
    
    # Create the folder if it doesn't exist
    video_dir = Path("hybrid_runs/videos")
    video_dir.mkdir(parents=True, exist_ok=True)
    
    # Check existing videos to find the next available number
    existing_videos = list(video_dir.glob("hybrid_*.mp4"))
    if existing_videos:
        nums = [int(p.stem.split('_')[-1]) for p in existing_videos if p.stem.split('_')[-1].isdigit()]
        next_vid_num = max(nums) + 1 if nums else 0
    else:
        next_vid_num = 0
        
    video_path = video_dir / f"hybrid_{next_vid_num}.mp4"
    
    # Let's use gray input since both environments natively output grayscale frame buffers
    video_writer = media.VideoWriter(str(video_path), (144, 160), fps=24, input_format="gray")
    video_writer.__enter__()

    print(f"Starting Hybrid AI Loop! Recording visually to: {video_path}")
    
    action_count = 0
    max_actions = 5000  # It will stop automatically after 5000 moves!
    
    try:
        while action_count < max_actions:
            action_count += 1
            
            # Check if we are in a battle by reading the RAM flag
            in_battle = pyboy.memory[0xD057] > 0
            
            # Save the current full-resolution frame to the video
            try:
                video_writer.add_image(pyboy.screen.ndarray[:,:,0])
            except BrokenPipeError:
                break
            
            if in_battle:
                # BATTLE AI
                # Battle env needs us to manually update its screen buffer before getting obs
                battle_env.update_recent_screens(battle_env.render())
                obs = battle_env._get_obs()
                
                # Since action needs to be a scalar, taking [0] if model returns array
                action, _ = battle_model.predict(obs)
                if isinstance(action, np.ndarray): action = int(action.item())
                
                battle_env._run_action(action)
                battle_env._update_recent_actions(action)
                
            else:
                # OVERWORLD AI
                # Overworld env natively updates its screen inside _get_obs()
                obs = overworld_env._get_obs()
                
                action, _ = overworld_model.predict(obs)
                if isinstance(action, np.ndarray): action = int(action.item())
                
                # The v2 exploration environment calls it 'run_action_on_emulator'
                overworld_env.run_action_on_emulator(action)
                overworld_env.update_recent_actions(action)

        print(f"\nSuccessfully hit {max_actions} actions! Safely wrapping up the video...")

    except KeyboardInterrupt:
        print(f"\nSaving the video early due to Ctrl+C...")
    finally:
        try:
            video_writer.close()
        except Exception:
            pass
        print(f"Saved to '{video_path}'!")

        # pyboy.tick() is handled natively by the run_action

if __name__ == "__main__":
    main()
    