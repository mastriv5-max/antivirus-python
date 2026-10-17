import os
import hashlib
import shutil
import json
from datetime import datetime

QUARANTINE_DIR = "quarantena"
REPORT_FILE = "report.json"
VIRUS_SIGNATURES = [
    b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
]

def get_file_hash(filepath):
    try:
        with open(filepath, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except:
        return None

def is_infected(filepath):
    try:
        with open(filepath, "rb") as f:
            content = f.read()
            for sig in VIRUS_SIGNATURES:
                if sig in content:
                    return True
        return False
    except:
        return False

def scan_folder(folder="."):
    if not os.path.exists(QUARANTINE_DIR):
        os.makedirs(QUARANTINE_DIR)
    
    files = []
    for root, dirs, filenames in os.walk(folder):
        if QUARANTINE_DIR in root:
            continue
        for name in filenames:
            if name == "antivirus.py":
                continue
            files.append(os.path.join(root, name))
    
    total = len(files)
    infected = []
    
    print(f"Scansione di {total} file in {folder}...")
    
    for i, filepath in enumerate(files):
        percent = int((i+1) / total * 100) if total > 0 else 100
        bar = "█" * (percent // 5) + "-" * (20 - percent // 5)
        print(f"\r[{bar}] {percent}% - {os.path.basename(filepath)[:30]}", end="")
        
        if is_infected(filepath):
            print(f"\nVIRUS TROVATO: {filepath}")
            dest = os.path.join(QUARANTINE_DIR, os.path.basename(filepath))
            try:
                shutil.move(filepath, dest)
                infected.append({
                    "file": filepath,
                    "quarantena": dest,
                    "hash": get_file_hash(dest),
                    "data": datetime.now().isoformat()
                })
                print(f"   -> Spostato in {QUARANTINE_DIR}/")
            except Exception as e:
                print(f"   -> Errore: {e}")
    
    print("\n\nScansione completata!")
    print(f"File infetti: {len(infected)}")
    
    with open(REPORT_FILE, "w") as f:
        json.dump(infected, f, indent=2)
    print(f"Report salvato in {REPORT_FILE}")
    return infected

def restore_file(filename):
    src = os.path.join(QUARANTINE_DIR, filename)
    if os.path.exists(src):
        shutil.move(src, filename)
        print(f"File {filename} ripristinato!")
        if os.path.exists(REPORT_FILE):
            with open(REPORT_FILE, "r") as f:
                data = json.load(f)
            data = [x for x in data if os.path.basename(x["file"]) != filename]
            with open(REPORT_FILE, "w") as f:
                json.dump(data, f, indent=2)
    else:
        print(f"File {filename} non trovato in quarantena")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "ripristina":
        if len(sys.argv) > 2:
            restore_file(sys.argv[2])
        else:
            print("Uso: python antivirus.py ripristina nomefile")
    else:
        scan_folder(".")
