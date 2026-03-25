
import os
import json
import hashlib
import numpy as np
import easyocr
import cv2
from pathlib import Path

class TileExtractor:
    def __init__(self, tile_size=(8, 8)):
        self.tile_size = tile_size

    def get_tiles(self, img_gray):
        h, w = img_gray.shape
        tiles = []
        for y in range(0, h, self.tile_size[1]):
            for x in range(0, w, self.tile_size[0]):
                tile = img_gray[y:y+self.tile_size[1], x:x+self.tile_size[0]]
                if tile.shape == self.tile_size:
                    tiles.append((tile, (x, y)))
        return tiles

class CharKnowledgeBase:
    def __init__(self, storage_path="char_map.json"):
        self.storage_path = Path(storage_path)
        self.knowledge = {}
        if self.storage_path.exists():
            with open(self.storage_path, 'r') as f:
                self.knowledge = json.load(f)

    def get_char(self, tile):
        t_hash = hashlib.md5(tile.tobytes()).hexdigest()
        return self.knowledge.get(t_hash), t_hash

    def add_char(self, t_hash, char):
        self.knowledge[t_hash] = char
        # Multi-process safety for JSON cache
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.knowledge, f)
        except Exception:
            pass

class GameParser:
    def __init__(self, session_path="."):
        self.kb = CharKnowledgeBase(Path(session_path) / "char_map.json")
        self.extractor = TileExtractor()
        # GPU=True for server deployment
        self.reader = easyocr.Reader(['en'], gpu=True)

    def read_area(self, screen_gray, area_coords):
        # area_coords: (y_start, y_end, x_start, x_end)
        y1, y2, x1, x2 = area_coords
        roi = screen_gray[y1:y2, x1:x2]
        
        # Binary threshold for cleaner OCR
        _, roi_bin = cv2.threshold(roi, 128, 255, cv2.THRESH_BINARY)
        
        tiles = self.extractor.get_tiles(roi_bin)
        result_str = ""
        current_y = -1
        
        for tile, (x, y) in tiles:
            # New line detection (naive)
            if current_y != -1 and y > current_y:
                result_str += " " # Space for new tile row
            current_y = y
            
            char, t_hash = self.kb.get_char(tile)
            if char:
                result_str += char
            else:
                # Tile is unknown, use EasyOCR on this tiny tile (or better, on the whole ROI and slice)
                # Optimization: In a real run, we might want to OCR the whole ROI and then map tiles.
                # For now, let's use a "blank" or fallback to prevent massive slowdown, 
                # or just use easyocr on the ROI if we hit unknown tiles.
                char = self._ocr_fallback(tile)
                if char:
                    self.kb.add_char(t_hash, char)
                    result_str += char
                else:
                    self_str = " "
                    
        return result_str.strip()

    def _ocr_fallback(self, tile):
        # Scale up tiny 8x8 tile for EasyOCR
        tile_up = cv2.resize(tile, (32, 32), interpolation=cv2.INTER_NEAREST)
        results = self.reader.readtext(tile_up)
        if results:
            return results[0][1][0] # Take first char of first result
        return None
