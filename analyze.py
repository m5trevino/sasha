import os
import sqlite3
import re

def setup_database(db_path="scripts/scripts.db"):
    """Initialize the SQLite database with necessary tables."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create Scripts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Scripts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        filepath TEXT,
        tags TEXT,
        original_name TEXT,
        size INTEGER
    )
    """)

    # Create Actions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action_name TEXT,
        script_id INTEGER,
        UNIQUE(action_name, script_id),
        FOREIGN KEY(script_id) REFERENCES Scripts(id)
    )
    """)

    conn.commit()
    conn.close()
    print("[INFO] Database setup completed.")

def extract_actions_from_script(script_path):
    """
    Analyze a script and extract actions based on patterns.
    Returns a dictionary with tags and actions.
    """
    actions = set()
    tags = set()

    try:
        with open(script_path, "r") as script_file:
            content = script_file.read()

            # Example: Detect Java Hooks
            if "Java.perform" in content or "Java.use" in content:
                tags.add("Java Hooks")
                actions.add("Java.perform")
                actions.add("Java.use")

            # Example: Detect Interceptor hooks
            if "Interceptor.attach" in content:
                tags.add("Interceptor Hooks")
                actions.add("Interceptor.attach")

            # Example: Detect SSL Pinning Bypass
            if "SSLContext" in content or "TrustManager" in content:
                tags.add("SSL Pinning Bypass")
                actions.add("SSLContext Hook")
                actions.add("TrustManager Hook")

            # Add more patterns here for additional tags/actions
            if "recv" in content or "send" in content:
                tags.add("Data Communication")
                actions.add("recv")
                actions.add("send")

            # General hooks or interesting keywords
            generic_keywords = ["hook", "bypass", "trace"]
            for keyword in generic_keywords:
                if keyword in content.lower():
                    tags.add(f"Generic-{keyword.capitalize()}")
                    actions.add(f"Generic-{keyword.capitalize()}")

    except Exception as e:
        print(f"[ERROR] Failed to analyze script {script_path}: {e}")

    return {
        "tags": list(tags),
        "actions": list(actions)
    }

def analyze_scripts(organized_dir="scripts/organized/general", db_path="scripts/scripts.db"):
    """Analyze all scripts in the organized directory and update the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all scripts in the directory
    scripts = [f for f in os.listdir(organized_dir) if f.endswith(".js")]
    if not scripts:
        print("[INFO] No scripts found in the organized directory.")
        return

    for script in scripts:
        script_path = os.path.join(organized_dir, script)

        # Extract features and tags
        analysis = extract_actions_from_script(script_path)
        tags = ", ".join(analysis["tags"])
        actions = analysis["actions"]

        # Insert script metadata into the Scripts table
        cursor.execute("""
        INSERT INTO Scripts (filename, filepath, tags, original_name, size)
        VALUES (?, ?, ?, ?, ?)
        """, (
            script,
            script_path,
            tags,
            script,  # Using the current name as the original name
            os.path.getsize(script_path)
        ))

        script_id = cursor.lastrowid  # Get the ID of the inserted script

        # Insert actions into the Actions table
        for action in actions:
            try:
                cursor.execute("""
                INSERT INTO Actions (action_name, script_id)
                VALUES (?, ?)
                """, (action, script_id))
            except sqlite3.IntegrityError:
                # Skip duplicates
                pass

        print(f"[INFO] Processed script: {script} (Tags: {tags})")

    conn.commit()
    conn.close()
    print("[INFO] Analysis completed and database updated.")

def main():
    """Main function to run the script analysis and tagging."""
    setup_database()  # Set up the database structure
    analyze_scripts()  # Analyze scripts in the organized/general directory

if __name__ == "__main__":
    main()
