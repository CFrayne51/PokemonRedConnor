import os
import sys
import argparse
from pathlib import Path
from pyboy import PyBoy

from red_gym.memory import PyBoyMemory
from red_gym.constants import DEFAULT_CONFIG

def wait_for_battle(pyboy, memory, max_wait=600):
    for i in range(max_wait):
        pyboy.tick(1, True)
        if memory.read_m(0xD057) > 0: # IN_BATTLE_FLAG
            return True
    return False

def generate_states(num_states, output_dir, gb_path="PokemonRed.gb", state_dir="v2/battle_states", headless=True):
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    in_dir = Path(state_dir)
    all_states = [str(s) for s in in_dir.glob("*.state") if not s.name.startswith("random_state_")]
    
    if not all_states:
        print(f"Error: No base states found in {state_dir}")
        return
        
    print(f"Generating {num_states} states in {out_dir} ...")
    
    pyboy = PyBoy(
        gb_path,
        window="null" if headless else "SDL2",
    )
    pyboy.set_emulation_speed(0 if headless else 6)
    
    memory = PyBoyMemory(pyboy)
    
    for i in range(num_states):
        # Load a random base state
        base_state = __import__("random").choice(all_states)
        with open(base_state, "rb") as f:
            pyboy.load_state(f)
            
        print(f"Generating state {i+1}/{num_states} ...", end="", flush=True)
        
        # 1. Wait for the battle transition to settle first
        # This ensures the game's internal initialization (which overwrites RAM) is finished.
        success = wait_for_battle(pyboy, memory)
        
        if not success:
            print(" [WARNING] Battle did not start within timeout. State might be invalid.")
            continue

        # 2. NOW inject the random pokemon into the established battle RAM
        memory.inject_ram()
        
        # 3. Give it a few frames to process the RAM change
        pyboy.tick(60, True)
        
        print(" [OK]")
            
        # Save the new state
        save_path = out_dir / f"random_state_{i:04d}.state"
        with open(save_path, "wb") as f:
            pyboy.save_state(f)
            
    pyboy.stop()
    print("Done generating states!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate randomized Pokemon Red battle states.")
    parser.add_argument("--num-states", type=int, default=100, help="Number of random states to generate")
    parser.add_argument("--output-dir", type=str, default="v2/battle_states", help="Directory to save states")
    parser.add_argument("--gb-path", type=str, default="PokemonRed.gb", help="Path to Pokemon Red ROM")
    parser.add_argument("--state-dir", type=str, default="v2/battle_states", help="Directory containing base save states")
    parser.add_argument("--show-window", action="store_true", help="Show PyBoy window while generating")
    
    args = parser.parse_args()
    
    generate_states(
        num_states=args.num_states,
        output_dir=args.output_dir,
        gb_path=args.gb_path,
        state_dir=args.state_dir,
        headless=not args.show_window
    )
