import os
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from red_gym.environment import RedGymEnv

def main():
    # Make sure we don't crash if the folder doesn't exist
    Path("viz_runs").mkdir(exist_ok=True)

    env_config = {
        'headless': True, 
        'save_final_state': False, 
        'early_stop': True,
        'action_freq': 60, 
        'max_steps': 100, 
        'print_rewards': False, 
        'save_video': False, 
        'fast_video': False, 
        'session_path': "viz_runs",
        'gb_path': 'PokemonRed.gb', 
        'debug': False, 
        'reward_scale': 0.5, 
        'explore_weight': 0.25,
        'randomize_pokemon': False
    }

    print("Initializing environment...")
    env = RedGymEnv(env_config)
    
    print("Resetting environment to get initial observation...")
    obs, info = env.reset()

    # The RL model sees a 72x80 shape split across stacks 
    # The 'screens' key holds this data. Shape is typically (72, 80, 3)
    screens = obs['screens']
    
    print(f"Observation 'screens' shape: {screens.shape}")
    
    print("Taking 100 random steps and saving on >=5% change...")
    
    last_saved_frame = None
    save_count = 0
    
    for i in range(100):
        obs, reward, terminated, truncated, info = env.step(env.action_space.sample())
        current_frame = obs['screens'][:, :, 2]
        
        if last_saved_frame is None:
            last_saved_frame = current_frame
            continue
            
        # Compare pixels
        diff = np.mean(current_frame != last_saved_frame)
        
        if diff >= 0.05:
            screens = obs['screens']
            fig, axes = plt.subplots(1, 3, figsize=(12, 5))
            fig.suptitle(f"Step {i} (Pixel Diff: {diff:.1%})", fontsize=16)

            axes[0].imshow(screens[:, :, 0], cmap='gray')
            axes[0].set_title("Frame -2 (Oldest)")
            axes[0].axis('off')

            axes[1].imshow(screens[:, :, 1], cmap='gray')
            axes[1].set_title("Frame -1")
            axes[1].axis('off')

            axes[2].imshow(screens[:, :, 2], cmap='gray')
            axes[2].set_title("Current Frame")
            axes[2].axis('off')

            plt.tight_layout()
            
            save_path = f"viz_runs/rl_vision_step_{i}.png"
            plt.savefig(save_path, facecolor='white')
            plt.close(fig)
            
            print(f"Saved {save_path} (Difference: {diff:.1%})")
            last_saved_frame = current_frame
            save_count += 1

    print(f"\nSuccess! Saved {save_count} images.")
    
    env.close()

if __name__ == "__main__":
    main()
