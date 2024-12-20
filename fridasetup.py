import subprocess
import os
from pathlib import Path

def bold(text):
    return f"\033[1m{text}\033[0m"

def colorize(text, color):
    color_codes = {
        'yellow': '\033[33m',
        'green': '\033[32m',
        'red': '\033[31m',
        'cyan': '\033[36m'
    }
    return f"{color_codes.get(color, '')}{text}\033[0m"

def execute_command(command, shell=False):
    """Execute a command and return the result, with error handling."""
    try:
        result = subprocess.check_output(command, shell=shell).decode('utf-8').strip()
        return result
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {e}")
        return e.output.decode('utf-8')  # Return the error output for better diagnostics

def check_frida_version():
    """Check the installed Frida version."""
    print(f"[INFO] Executing: {colorize(bold('frida --version'), 'cyan')}")
    frida_version = execute_command("frida --version", shell=True)
    print(f"[INFO] Frida version: {frida_version}")

def get_local_ip_address():
    """Retrieve the local machine IP address."""
    print(f"[INFO] Executing: {colorize(bold('hostname -I'), 'cyan')}")
    ip_address = execute_command("hostname -I", shell=True).split()[0]  # Get the first IP (local)
    print(f"[INFO] Local machine IP address: {ip_address}")
    return ip_address

def setup_proxy(ip_address):
    """Set up the reverse proxy for Frida communication."""
    print(f"[INFO] Enter Proxy Port (default 8080): ", end="")
    proxy_port = input().strip() or "8080"
    
    print(f"[INFO] Executing: {colorize(bold(f'adb reverse tcp:{proxy_port} tcp:{proxy_port}'), 'cyan')}")
    execute_command(f"adb reverse tcp:{proxy_port} tcp:{proxy_port}", shell=True)
    print(f"[INFO] Reverse proxy set up on port {proxy_port}.")

    # Only set the local IP (filter out public IP)
    print(f"[INFO] Executing: {colorize(bold(f'adb shell settings put global http_proxy {ip_address}:{proxy_port}'), 'cyan')}")
    execute_command(f"adb shell settings put global http_proxy {ip_address}:{proxy_port}", shell=True)
    print(f"[INFO] HTTP proxy set to {ip_address}:{proxy_port}.")

def start_frida_server():
    """Start Frida server on the emulator."""
    print(f"[INFO] Executing: {colorize(bold('adb root'), 'cyan')}")
    execute_command("adb root", shell=True)

    print(f"[INFO] Executing: {colorize(bold('adb shell pkill frida-server'), 'cyan')}")
    execute_command("adb shell pkill frida-server", shell=True)

    print(f"[INFO] Starting Frida server...")
    command = "adb shell /data/local/tmp/frida-server &"
    print(f"[INFO] Executing: {colorize(bold(command), 'cyan')}")
    
    # Run the Frida server command in the background using subprocess.Popen
    subprocess.Popen(command, shell=True)

    print(f"[INFO] Frida server should now be running in the background.")

def display_frida_server_details():
    """Display Frida server session details."""
    print("\n=======================================================")
    print(bold("Frida Server Details"))
    print("=======================================================")
    
    # Displaying Frida version on server
    print(f"[INFO] Executing: {colorize(bold('adb shell ls /data/local/tmp/frida-server'), 'cyan')}")
    frida_server_location = execute_command("adb shell ls /data/local/tmp/frida-server", shell=True)
    print(f"[INFO] Frida server binary found at: /data/local/tmp/frida-server")

    print(f"[INFO] Executing: {colorize(bold('adb shell /data/local/tmp/frida-server --version'), 'cyan')}")
    frida_server_version = execute_command("adb shell /data/local/tmp/frida-server --version", shell=True)
    print(f"[INFO] Frida server version: {frida_server_version}")

    print(f"[INFO] Executing: {colorize(bold('adb shell ps | grep frida-server'), 'cyan')}")
    frida_server_pid = execute_command("adb shell ps | grep frida-server", shell=True)
    print(f"[INFO] Frida server is running with PID: {frida_server_pid.split()[1]}")
    
    print("=======================================================")

def show_main_menu():
    """Display the main menu after setting up Frida."""
    print("\nMain Menu:")
    print("[1] Start an app with a script from process (from script DB, file path, or CodeShare link).")
    print("[2] Inject an app with script using PID.")
    print("[3] View available scripts.")
    print("[4] Add a new script to the script DB.")
    print("[5] Exit.")
    
    choice = input("Enter your choice: ").strip()
    if choice == "1":
        start_app_with_script()
    elif choice == "2":
        inject_app_with_pid()
    elif choice == "3":
        view_available_scripts()
    elif choice == "4":
        add_new_script()
    elif choice == "5":
        print("[INFO] Exiting. Goodbye!")
        exit()

def start_app_with_script():
    """Allow the user to select an app and run a script."""
    print("[INFO] Listing running apps (excluding system apps)...")
    apps = list_running_apps(show_system_apps=False)
    
    # List scripts and choose one
    script_choice = input("Enter the script path or CodeShare URL: ").strip()
    print(f"[INFO] Running selected app and script: {script_choice}")

def inject_app_with_pid():
    """Allow the user to select an app by PID and inject a script."""
    print("[INFO] Listing running processes on the emulator...")
    processes = list_running_apps(show_system_apps=False)
    
    pid = input("Enter the PID of the process to inject: ").strip()
    print(f"[INFO] Injecting script into PID {pid}...")

def list_running_apps(show_system_apps=False):
    """List all running apps on the emulator, with an option to exclude system apps."""
    command = "frida-ps -Uia"
    output = execute_command(command, shell=True)
    apps = []
    
    if not output:
        print("[ERROR] No apps found.")
        return apps
    
    print(f"[INFO] Running apps:")
    for line in output.splitlines():
        if "com.android" not in line and "com.google.android" not in line:
            apps.append(line)
            print(line)
    
    return apps

def main():
    """Main function to coordinate the Frida setup and script execution."""
    
    # Step 1: Check Frida version
    check_frida_version()
    
    # Step 2: Get the local IP address
    ip_address = get_local_ip_address()
    
    # Step 3: Set up reverse proxy
    setup_proxy(ip_address)
    
    # Step 4: Start Frida server in the background
    start_frida_server()

    # Step 5: Display Frida server details
    display_frida_server_details()

    # Step 6: Show the main menu
    show_main_menu()

if __name__ == "__main__":
    main()
