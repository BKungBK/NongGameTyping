import json
import os
import random
import shutil
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass

class Rarity(Enum):
    R = "R"
    SR = "SR"
    SSR = "SSR"

@dataclass
class Item:
    name: str
    icon: str
    rarity: Rarity
    rate: float
    is_owned: bool = False
    
    def get_rarity_color(self) -> tuple:
        colors = {
            Rarity.R: (100, 149, 237),      # Cornflower Blue
            Rarity.SR: (147, 112, 219),     # Medium Slate Blue
            Rarity.SSR: (255, 215, 0)       # Gold
        }
        return colors[self.rarity]

class DataManager:
    """Centralized data management for all game data"""
    
    def __init__(self):
        # Setup data directory in user's home
        self.home_dir = os.path.expanduser("~")
        self.data_dir = os.path.join(self.home_dir, "NongGameTyping")
        
        # Define all directory paths first
        self.settings_dir = os.path.join(self.data_dir, "setting")
        self.data_dir_path = os.path.join(self.data_dir, "data")
        self.assets_dir = os.path.join(self.data_dir, "assets")
        self.fonts_dir = os.path.join(self.assets_dir, "fonts")
        self.images_dir = os.path.join(self.assets_dir, "images")
        self.sounds_dir = os.path.join(self.assets_dir, "sounds")
        
        # Define file paths
        self.settings_path = os.path.join(self.settings_dir, "setting.json")
        self.gacha_data_path = os.path.join(self.data_dir_path, "gacha_data.json")
        self.word_data_path = os.path.join(self.data_dir_path, "word.json")
        
        # Create directory structure
        self._ensure_directory_structure()
        
        # Initialize data
        self.gacha_data = {}
        self.words = []
        self.settings = {}
        
        # Load all data
        self._load_all_data()
    
    def _ensure_directory_structure(self):
        """Ensure all necessary directories exist"""
        directories = [
            self.data_dir,
            self.settings_dir,
            self.data_dir_path,
            self.assets_dir,
            self.fonts_dir,
            self.images_dir,
            self.sounds_dir
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created directory: {directory}")
        
        # Copy assets if needed
        self._copy_assets_if_needed()
    
    def _copy_assets_if_needed(self):
        """Copy assets from project directory to user's home directory if they don't exist"""
        # Define source and destination mappings
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        asset_mappings = [
            (os.path.join(project_root, "assets", "fonts"), self.fonts_dir),
            (os.path.join(project_root, "assets", "images"), self.images_dir),
            (os.path.join(project_root, "assets", "sounds"), self.sounds_dir)
        ]
        
        for src_dir, dst_dir in asset_mappings:
            if os.path.exists(src_dir) and not os.path.exists(dst_dir):
                try:
                    shutil.copytree(src_dir, dst_dir)
                    print(f"Copied assets from {src_dir} to {dst_dir}")
                except Exception as e:
                    print(f"Error copying assets from {src_dir}: {e}")
            elif os.path.exists(src_dir):
                # Copy individual files if directory exists but files might be missing
                try:
                    for item in os.listdir(src_dir):
                        src_item = os.path.join(src_dir, item)
                        dst_item = os.path.join(dst_dir, item)
                        if os.path.isfile(src_item) and not os.path.exists(dst_item):
                            shutil.copy2(src_item, dst_item)
                            print(f"Copied file: {item}")
                        elif os.path.isdir(src_item) and not os.path.exists(dst_item):
                            shutil.copytree(src_item, dst_item)
                            print(f"Copied directory: {item}")
                except Exception as e:
                    print(f"Error copying individual assets from {src_dir}: {e}")
    
    def _load_all_data(self):
        """Load all game data files"""
        self._load_gacha_data()
        self._load_word_data()
        self._load_settings()
    
    def _load_gacha_data(self):
        """Load or create gacha data"""
        try:
            if os.path.exists(self.gacha_data_path):
                with open(self.gacha_data_path, "r", encoding="utf-8") as f:
                    self.gacha_data = json.load(f)
                print(f"Loaded gacha data from: {self.gacha_data_path}")
            else:
                self._create_default_gacha_data()
        except Exception as e:
            print(f"Error loading gacha data: {e}")
            self._create_default_gacha_data()
    
    def _create_default_gacha_data(self):
        """Create default gacha data with is_owned field"""
        self.gacha_data = {
            "items": {
                "SSR": [
                    {"name": "Excalibur", "icon": "excalibur.png", "rate": 1.0, "is_owned": False},
                    {"name": "Phoenix Wing", "icon": "phoenix_wing.png", "rate": 1.0, "is_owned": False},
                    {"name": "Dragon Scale", "icon": "dragon_scale.png", "rate": 1.0, "is_owned": False},
                    {"name": "Divine Staff", "icon": "divine_staff.png", "rate": 1.5, "is_owned": False},
                    {"name": "Time Crystal", "icon": "time_crystal.png", "rate": 0.5, "is_owned": False}
                ],
                "SR": [
                    {"name": "Magic Bow", "icon": "magic_bow.png", "rate": 3.0, "is_owned": False},
                    {"name": "Crystal Wand", "icon": "crystal_wand.png", "rate": 3.0, "is_owned": False},
                    {"name": "Shadow Cloak", "icon": "shadow_cloak.png", "rate": 3.0, "is_owned": False},
                    {"name": "Thunder Hammer", "icon": "thunder_hammer.png", "rate": 4.0, "is_owned": False},
                    {"name": "Ice Shield", "icon": "ice_shield.png", "rate": 2.0, "is_owned": False}
                ],
                "R": [
                    {"name": "Iron Sword", "icon": "iron_sword.png", "rate": 15.0, "is_owned": False},
                    {"name": "Wooden Staff", "icon": "wooden_staff.png", "rate": 15.0, "is_owned": False},
                    {"name": "Leather Armor", "icon": "leather_armor.png", "rate": 15.0, "is_owned": False},
                    {"name": "Silver Ring", "icon": "silver_ring.png", "rate": 20.0, "is_owned": False},
                    {"name": "Health Potion", "icon": "health_potion.png", "rate": 15.0, "is_owned": False},
                    {"name": "Magic Scroll", "icon": "magic_scroll.png", "rate": 15.0, "is_owned": False}
                ]
            },
            "base_rates": {
                "SSR": 5.0,
                "SR": 15.0,
                "R": 80.0
            }
        }
        self._save_gacha_data()
        print(f"Created default gacha data at: {self.gacha_data_path}")
    
    def _save_gacha_data(self):
        """Save gacha data to file"""
        try:
            with open(self.gacha_data_path, "w", encoding="utf-8") as f:
                json.dump(self.gacha_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving gacha data: {e}")
    
    def _load_word_data(self):
        """Load or create word data"""
        try:
            if os.path.exists(self.word_data_path):
                with open(self.word_data_path, "r", encoding="utf-8") as f:
                    self.words = json.load(f)
                print(f"Loaded word data from: {self.word_data_path}")
            else:
                self._create_default_word_data()
        except Exception as e:
            print(f"Error loading word data: {e}")
            self._create_default_word_data()
    
    def _create_default_word_data(self):
        """Create default word data"""
        self.words = [
            "hello", "world", "python", "game", "typing", "speed", "test",
            "computer", "programming", "development", "software", "application",
            "database", "network", "internet", "website", "server", "client",
            "algorithm", "function", "variable", "class", "object", "method",
            "interface", "library", "framework", "api", "sdk", "plugin",
            "module", "package", "repository", "version", "control", "git",
            "github", "bitbucket", "gitlab", "deployment", "production",
            "testing", "debugging", "optimization", "performance", "security",
            "authentication", "authorization", "encryption", "decryption",
            "compression", "decompression", "serialization", "deserialization"
        ]
        self._save_word_data()
        print(f"Created default word data at: {self.word_data_path}")
    
    def _save_word_data(self):
        """Save word data to file"""
        try:
            with open(self.word_data_path, "w", encoding="utf-8") as f:
                json.dump(self.words, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving word data: {e}")
    
    def _load_settings(self):
        """Load or create settings data"""
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    self.settings = json.load(f)
                print(f"Loaded settings from: {self.settings_path}")
            else:
                self._create_default_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            self._create_default_settings()
    
    def _create_default_settings(self):
        """Create default settings"""
        self.settings = {
            'screen_width': 1280,
            'screen_height': 720,
            'fps': 60,
            'max_time_per_word': 20,
            'growth_on_success': 0.15,
            'growth_on_error': -0.05,
            'growth_timer_interval': 5.0,
            'growth_per_interval': 0.01,
            'coins_per_growth': 5,
            'coins': 1000,  # เพิ่มค่าเริ่มต้นสำหรับเงิน
            'sound_volume': 0.5,
            'music_volume': 0.3,
            'difficulty': 'normal',
            'language': 'en',
            # Game statistics
            'total_words_typed': 0,
            'total_coins_earned': 0,
            'best_combo': 0
        }
        self._save_settings()
        print(f"Created default settings at: {self.settings_path}")
    
    def _save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    # Public methods for accessing data
    
    def get_gacha_data(self) -> Dict[str, Any]:
        """Get gacha data"""
        return self.gacha_data
    
    def get_words(self) -> List[str]:
        """Get word list"""
        return self.words
    
    def get_settings(self) -> Dict[str, Any]:
        """Get settings"""
        return self.settings
    
    def get_random_word(self) -> str:
        """Get a random word from the word list"""
        return random.choice(self.words) if self.words else "default"
    
    def set_item_ownership(self, item_name: str, rarity: Rarity, is_owned: bool) -> bool:
        """Set ownership status of an item"""
        try:
            rarity_str = rarity.value
            if rarity_str in self.gacha_data.get("items", {}):
                for item in self.gacha_data["items"][rarity_str]:
                    if item["name"] == item_name:
                        item["is_owned"] = is_owned
                        self._save_gacha_data()
                        return True
            return False
        except Exception as e:
            print(f"Error setting item ownership: {e}")
            return False

    def add_item_to_collection(self, item_name: str, rarity: Rarity) -> bool:
        """Add an item to player's collection (mark as owned)"""
        return self.set_item_ownership(item_name, rarity, True)

    def get_player_stats(self) -> Dict[str, Any]:
        """Get player statistics"""
        try:
            total_items = 0
            owned_items = 0
            rarity_counts = {"R": 0, "SR": 0, "SSR": 0}
            owned_rarity_counts = {"R": 0, "SR": 0, "SSR": 0}
            
            for rarity_str, items in self.gacha_data.get("items", {}).items():
                for item in items:
                    total_items += 1
                    rarity_counts[rarity_str] += 1
                    if item.get("is_owned", False):
                        owned_items += 1
                        owned_rarity_counts[rarity_str] += 1
            
            completion_rate = (owned_items / total_items * 100) if total_items > 0 else 0
            
            return {
                "total_items": total_items,
                "owned_items": owned_items,
                "completion_rate": round(completion_rate, 1),
                "rarity_counts": rarity_counts,
                "owned_rarity_counts": owned_rarity_counts
            }
        except Exception as e:
            print(f"Error getting player stats: {e}")
            return {
                "total_items": 0,
                "owned_items": 0,
                "completion_rate": 0,
                "rarity_counts": {"R": 0, "SR": 0, "SSR": 0},
                "owned_rarity_counts": {"R": 0, "SR": 0, "SSR": 0}
            }
    
    def get_items_by_rarity(self, rarity: Rarity) -> List[Item]:
        """Get items by rarity with ownership status"""
        items = []
        if rarity.value in self.gacha_data["items"]:
            for item_data in self.gacha_data["items"][rarity.value]:
                item = Item(
                    name=item_data["name"],
                    icon=item_data["icon"],
                    rarity=rarity,
                    rate=item_data["rate"],
                    is_owned=item_data.get("is_owned", False)
                )
                items.append(item)
        return items
    
    def get_all_items(self) -> List[Item]:
        """Get all items with ownership status"""
        all_items = []
        for rarity_str in ["R", "SR", "SSR"]:
            try:
                rarity = Rarity(rarity_str)
                all_items.extend(self.get_items_by_rarity(rarity))
            except ValueError:
                continue
        return all_items
    
    def get_collected_items(self) -> List[Item]:
        """Get all collected items"""
        return [item for item in self.get_all_items() if item.is_owned]
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        stats = {"total": 0, "collected": 0}
        for rarity_str in ["R", "SR", "SSR"]:
            try:
                rarity = Rarity(rarity_str)
                items = self.get_items_by_rarity(rarity)
                stats[rarity_str] = {"total": len(items), "collected": 0}
                stats["total"] += len(items)
                for item in items:
                    if item.is_owned:
                        stats[rarity_str]["collected"] += 1
                        stats["collected"] += 1
            except ValueError:
                continue
        return stats
    
    def update_settings(self, new_settings: Dict[str, Any]):
        """Update settings"""
        self.settings.update(new_settings)
        self._save_settings()
    
    def reset_all_data(self):
        """Reset all data to default (for testing/debugging)"""
        self._create_default_gacha_data()
        self._create_default_word_data()
        self._create_default_settings()
        print("All data reset to default values")
    
    def get_assets_path(self, asset_type: str, filename: str = None) -> str:
        """Get the path to assets in the user's home directory"""
        asset_paths = {
            "fonts": self.fonts_dir,
            "images": self.images_dir,
            "sounds": self.sounds_dir
        }
        
        if asset_type not in asset_paths:
            raise ValueError(f"Invalid asset type: {asset_type}")
        
        if filename:
            return os.path.join(asset_paths[asset_type], filename)
        return asset_paths[asset_type]

    def get_save_path(self):
        """Return the path to save.json in the data directory"""
        return os.path.join(self.data_dir_path, "save.json")

    def load_autosave(self):
        """Load autosave data from save.json if exists, else return None"""
        save_path = self.get_save_path()
        if os.path.exists(save_path):
            try:
                with open(save_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading autosave: {e}")
        return None

    def save_autosave(self, coins, combo, plant_growth):
        """Save autosave data to save.json"""
        save_path = self.get_save_path()
        data = {
            "coins": coins,
            "combo": combo,
            "plant_growth": plant_growth
        }
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving autosave: {e}") 