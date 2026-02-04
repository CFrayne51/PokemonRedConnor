
import hashlib
import json
import os
import cv2
import numpy as np
import easyocr

class TileExtractor:
    """
    Component: TILE EXTRACTOR
    Purpose: Isolates individual characters from a larger image region.
    """
    @staticmethod
    def extract_tiles(image_region):
        tiles = []
        
        if len(image_region.shape) == 3:
            gray = cv2.cvtColor(image_region, cv2.COLOR_BGR2GRAY)
        else:
            gray = image_region
            
        _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV)
        
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        bounding_boxes = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 1 and h > 1: 
                bounding_boxes.append((x, y, w, h))
        
        bounding_boxes.sort(key=lambda b: b[0])
        
        for (x, y, w, h) in bounding_boxes:
            roi = image_region[y:y+h, x:x+w]
            pad = 2
            
            has_color = len(roi.shape) == 3
            if has_color:
                h_roi, w_roi, c_roi = roi.shape
                bg_color = tuple([255] * c_roi)
                padded = np.full((h + 2*pad, w + 2*pad, c_roi), bg_color, dtype=np.uint8)
            else:
                bg_color = 255
                padded = np.full((h + 2*pad, w + 2*pad), bg_color, dtype=np.uint8)
                
            padded[pad:pad+h, pad:pad+w] = roi

            tiles.append({
                'image': padded,
                'row': 0, 
                'col': x 
            })
            
        return tiles

class CharKnowledgeBase:
    """
    Component: KNOWLEDGE BASE (Persistent Memory)
    """
    def __init__(self, map_file='char_map.json'):
        self.map_file = map_file
        self.char_map = self._load_map()
        self.unsaved_changes = False

    def _load_map(self):
        if os.path.exists(self.map_file):
            try:
                with open(self.map_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading KB: {e}")
                return {}
        return {}

    def save(self):
        if self.unsaved_changes:
            with open(self.map_file, 'w', encoding='utf-8') as f:
                json.dump(self.char_map, f, indent=2, sort_keys=True)
            self.unsaved_changes = False

    def get_char(self, img_hash):
        return self.char_map.get(img_hash)

    def set_char(self, img_hash, char):
        if self.char_map.get(img_hash) != char:
            self.char_map[img_hash] = char
            self.unsaved_changes = True

class UnknownTileManager:
    """
    Component: MANUAL REVIEW QUEUE
    """
    def __init__(self, output_dir='unknown_tiles'):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def save_tile(self, tile_img, img_hash):
        path = os.path.join(self.output_dir, f"{img_hash}.png")
        if not os.path.exists(path):
            scale = 8
            h, w = tile_img.shape[:2]
            upscaled = cv2.resize(tile_img, (w * scale, h * scale), interpolation=cv2.INTER_NEAREST)
            cv2.imwrite(path, upscaled)

class FastGuesser:
    """
    Component: FAST OCR GUESSER
    """
    def __init__(self):
        print("Initializing EasyOCR...")
        self.reader = easyocr.Reader(['en'], gpu=True, verbose=False)

    def guess(self, tile_img):
        scale = 8
        h, w = tile_img.shape[:2]
        upscaled = cv2.resize(tile_img, (w * scale, h * scale), interpolation=cv2.INTER_NEAREST)
        
        try:
            results = self.reader.readtext(upscaled, detail=0)
            if results:
                return results[0] 
            return "?" 
        except:
            return "?"

class GameParser:
    """
    Component: MAIN OCR CONTROLLER
    """
    def __init__(self):
        self.kb = CharKnowledgeBase()
        self.tile_manager = UnknownTileManager()
        self.guesser = FastGuesser()

    def read_area(self, screen, coords):
        y1, y2, x1, x2 = coords
        region = screen[y1:y2, x1:x2]
        
        # Check if region is effectively empty/black before trying to read
        if np.mean(region) < 10: 
            return ""

        tiles = TileExtractor.extract_tiles(region)
        
        result_text = ""
        
        for tile_data in tiles:
            tile_img = tile_data['image']
            img_bytes = np.ascontiguousarray(tile_img).tobytes()
            img_hash = hashlib.sha256(img_bytes).hexdigest()
            
            known_char = self.kb.get_char(img_hash)
            
            if known_char is not None:
                char = known_char
            else:
                if np.std(tile_img) < 5 and np.mean(tile_img) > 200:
                    char = " "
                    self.kb.set_char(img_hash, char) 
                else:
                    guess = self.guesser.guess(tile_img)
                    char = guess
                    self.tile_manager.save_tile(tile_img, img_hash)
                    self.kb.set_char(img_hash, char)
            
            result_text += char
            
        self.kb.save()
        return result_text
