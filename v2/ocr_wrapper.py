
import gymnasium as gym
import numpy as np
from gymnasium import spaces
from ocr import GameParser
from pokemon_data import MOVES_MAP

class PokemonOCRWrapper(gym.ObservationWrapper):
    def __init__(self, env):
        super().__init__(env)
        self.parser = GameParser()
        # Define areas for Move Names (Approximate coordinates for standard battle UI)
        # Using the standard text box area which overlaps with Fight Menu
        self.text_area_coords = (112, 144, 8, 160) # Expanded slightly to catch more text lines
        
        # Update Observation Space to include 'move_ids'
        # We return a fixed size array of 4 IDs (0 if not found)
        # This matches the user's request for "embedding the 4 Move IDs"
        new_spaces = env.observation_space.spaces.copy()
        new_spaces['move_ids'] = spaces.Box(low=0, high=255, shape=(4,), dtype=np.int32)
        self.observation_space = spaces.Dict(new_spaces)
        
    def observation(self, obs):
        screen = obs['screens'][:, :, 0] # Use only the most recent frame
        
        # Read text from screen
        text = self.parser.read_area(screen, self.text_area_coords)
        
        # Map found text to Move IDs
        found_ids = []
        text_upper = text.upper()
        
        # Naive keyword matching: check if any known Move Name appears in the OCR text
        # This allows us to catch "SURF" even if the text is "USE SURF"
        for move_name, move_id in MOVES_MAP.items():
            if move_name in text_upper:
                found_ids.append(move_id)
        
        # Pad with 0s (No Move) or truncate to 4
        # We prioritize the first found moves
        if len(found_ids) < 4:
            found_ids += [0] * (4 - len(found_ids))
        else:
            found_ids = found_ids[:4]
            
        # Add to observation
        obs['move_ids'] = np.array(found_ids, dtype=np.int32)
        
        # Optional: Keep raw text for debug if needed, but remove if it breaks SB3 policies requiring numeric only
        # obs['text'] = text 
        
        return obs
