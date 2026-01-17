import os
import json
import random
import glob
import sys
import io

# Force UTF-8 output for Windows terminals
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration
BASE_INSTRUCTION_FILE = "AIプロンプト作成指示書.md"
CONFIG_FILE = "prompt_config.json"
STORY_DIR = "ストーリー"
CHAR_SETTING_DIR = "キャラクター設定"

def load_file_content(filepath):
    """Loads text content from a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return ""

def load_config():
    """Loads the JSON configuration file."""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config file {CONFIG_FILE} not found.")
        return {"situations": [], "play_contents": []}
    except json.JSONDecodeError:
        print(f"Error decoding {CONFIG_FILE}.")
        return {"situations": [], "play_contents": []}

def find_character_files():
    """Scans directories for character profile Markdown files."""
    char_files = []
    
    # 1. Search in キャラクター設定 (root level)
    if os.path.exists(CHAR_SETTING_DIR):
        for filepath in glob.glob(os.path.join(CHAR_SETTING_DIR, "*.md")):
             char_files.append(filepath)

    # 2. Search in ストーリー subdirectories
    if os.path.exists(STORY_DIR):
        for root, dirs, files in os.walk(STORY_DIR):
            # Check if current directory is '00_設定資料' or 'キャラクター設定' (just in case)
            dir_name = os.path.basename(root)
            
            # Condition: In '00_設定資料' folder OR file ends with '_プロフィール.md'
            # Note: The prompt plan says: "Files inside 00_設定資料, キャラクター設定 folders, or files ending in _プロフィール.md"
            
            for file in files:
                if not file.endswith(".md"):
                    continue
                
                filepath = os.path.join(root, file)
                
                if dir_name == "00_設定資料" or dir_name == "キャラクター設定":
                    char_files.append(filepath)
                elif file.endswith("_プロフィール.md"):
                    char_files.append(filepath)

    # Remove duplicates if any
    return list(set(char_files))

def main():
    # 1. Load Base Instruction
    base_instruction = load_file_content(BASE_INSTRUCTION_FILE)
    if not base_instruction:
        print("Base instruction not found. Make sure 'AIプロンプト作成指示書.md' exists.")
        return

    # 2. Load Config
    config = load_config()
    situations = config.get("situations", [])
    play_contents = config.get("play_contents", [])

    if not situations:
        situations = ["指定なし"]
    if not play_contents:
        play_contents = ["指定なし"]

    # 3. Find Character Files
    char_files = find_character_files()
    if not char_files:
        print("No character profile files found.")
        return

    # 4. Random Selection
    selected_char_file = random.choice(char_files)
    selected_situation = random.choice(situations)
    selected_play = random.choice(play_contents)

    # Load Character Profile
    char_profile = load_file_content(selected_char_file)

    # 5. Output Generation
    output = f"""{base_instruction}

---

# Target Character (Source: {selected_char_file})
{char_profile}

# Situation
{selected_situation}

# Play Content
{selected_play}
"""
    print(output)

if __name__ == "__main__":
    main()
