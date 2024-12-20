import os
import shutil
import hashlib

# Helper functions...

def setup_directories(base_dir="scripts"):
    """Set up the directory structure for organizing scripts."""
    subdirs = ["raw", "backup", "organized", "dupe"]
    for subdir in subdirs:
        os.makedirs(os.path.join(base_dir, subdir), exist_ok=True)
    print("[INFO] Directory structure set up.")

def calculate_file_hash(file_path):
    """Calculate the SHA256 hash of a file."""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def handle_duplicates(raw_dir="scripts/raw", dupe_dir="scripts/dupe"):
    """Identify and handle duplicate scripts."""
    os.makedirs(dupe_dir, exist_ok=True)
    hashes = {}
    duplicates = []

    for script in os.listdir(raw_dir):
        if script.endswith(".js"):
            script_path = os.path.join(raw_dir, script)
            file_hash = calculate_file_hash(script_path)

            if file_hash in hashes:
                duplicates.append((script, hashes[file_hash]))
                dest_path = os.path.join(dupe_dir, script)
                shutil.move(script_path, dest_path)
                print(f"[INFO] Moved duplicate script {script} to {dupe_dir}.")
            else:
                hashes[file_hash] = script

    if duplicates:
        print("[INFO] Duplicate scripts detected and moved:")
        for dup, original in duplicates:
            print(f"  - Duplicate: {dup}, Original: {original}")
    else:
        print("[INFO] No duplicate scripts found.")

def backup_script(script, source_dir="scripts/raw", backup_dir="scripts/backup"):
    """Backup the script to the backup directory."""
    os.makedirs(backup_dir, exist_ok=True)
    source_path = os.path.join(source_dir, script)
    backup_path = os.path.join(backup_dir, script)
    shutil.copy2(source_path, backup_path)
    print(f"[INFO] Backed up {script} to {backup_dir}.")

def clean_script(script, source_dir="scripts/raw", organized_dir="scripts/organized"):
    """Clean the script and organize based on tags."""
    os.makedirs(organized_dir, exist_ok=True)
    source_path = os.path.join(source_dir, script)

    try:
        with open(source_path, "r") as f:
            content = f.read()
    except Exception as e:
        print(f"[ERROR] Failed to read {script}: {e}")
        return

    dest_dir = os.path.join(organized_dir, "general")
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, script)
    shutil.copy2(source_path, dest_path)
    print(f"[INFO] Organized {script} into {dest_dir}.")

def process_scripts(base_dir="scripts"):
    """Process all scripts in the raw directory."""
    raw_dir = os.path.join(base_dir, "raw")
    backup_dir = os.path.join(base_dir, "backup")
    organized_dir = os.path.join(base_dir, "organized")
    dupe_dir = os.path.join(base_dir, "dupe")

    print(f"[DEBUG] Raw directory: {raw_dir}")
    print(f"[DEBUG] Backup directory: {backup_dir}")
    print(f"[DEBUG] Organized directory: {organized_dir}")
    print(f"[DEBUG] Dupe directory: {dupe_dir}")

    # Step 1: Handle duplicates
    print("[DEBUG] Handling duplicates...")
    handle_duplicates(raw_dir, dupe_dir)

    # Step 2: Proceed with backup and cleaning
    print("[DEBUG] Checking for scripts in raw directory...")
    scripts = [f for f in os.listdir(raw_dir) if f.endswith(".js")]
    print(f"[DEBUG] Found {len(scripts)} scripts in raw directory: {scripts}")
    if not scripts:
        print("[INFO] No scripts found in the raw directory.")
        return

    for script in scripts:
        print(f"[DEBUG] Processing script: {script}")
        backup_script(script, source_dir=raw_dir, backup_dir=backup_dir)
        clean_script(script, source_dir=raw_dir, organized_dir=organized_dir)

if __name__ == "__main__":
    setup_directories()  # Ensure directories exist
    process_scripts()    # Run the main processing
