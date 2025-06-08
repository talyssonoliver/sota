#!/usr/bin/env python3
"""
Debug configuration loading
"""
import json
import os
from pathlib import Path

config_path = "config/daily_cycle.json"

print(f"Config file exists: {os.path.exists(config_path)}")
print(f"Config file path: {Path(config_path).absolute()}")

try:
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"Raw content length: {len(content)}")
        print("First 200 chars:")
        print(repr(content[:200]))
        
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        print(f"Loaded config keys: {list(config.keys())}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
