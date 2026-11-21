import json, glob
[print(f"{f}, {len(json.load(open(f, encoding='utf-8')))}") for f in sorted(glob.glob('data/raw/2026-10-29/*.json'))]