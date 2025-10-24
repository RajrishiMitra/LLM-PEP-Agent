import os
import json
import numpy as np
from datetime import datetime

def convert_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Type {type(obj)} not serializable")

def write_md_to_txt(text: str, filename: str, base_path: str):
    os.makedirs(base_path, exist_ok=True)
    file_path = os.path.join(base_path, f"{filename[:60]}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"[INFO] Report saved: {file_path}")
    return file_path
