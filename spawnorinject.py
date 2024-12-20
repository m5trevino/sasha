import subprocess

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
        return None

def list_running_apps(show_system_apps=False):
    """List all running apps on the emulator, with an option to exclude system apps."""
    command = "frida-ps -Uia"
    output = execute_command(command, shell=True)
    apps = []
    
    if not output:
        print("[ERROR] Failed to retrieve the list of running apps. Ensure Frida is running and try again.")
        return apps

    print(f"[INFO] Running apps:")
    lines = output.splitlines()
    for index, line in enumerate(lines[1:], start=1):  # Skipping the header line
        if "com.android" not in line and "com.google.android" not in line:  # Exclude system apps
            formatted_line = f"{index}. {line}"
            if index % 2 == 0:  # Alternate between regular and bold text
                print(formatted_line)
            else:
                print(bold(formatted_line))
            apps.append(line)
    
    return apps

def spawn_app_with_script():
    """Allow the user to select an app package to spawn and run a script."""
    print("[INFO] Listing running apps (excluding system apps)...")
    apps = list_running_apps(show_system_apps=False)
    
    # Prompt for app selection
    if not apps:
        print("[ERROR] No apps found to spawn.")
        return

    try:
        app_index = int(input("\nEnter the number corresponding to the app you want to spawn: ").strip())
        selected_app = apps[app_index - 1]
        package_name = selected_app.split()[-1]  # Extract package name
    except (ValueError, IndexError):
        print("[ERROR] Invalid selection. Please try again.")
        return

    # Prompt for script file or CodeShare URL
    script_choice = input("Enter the script file path or CodeShare URL: ").strip()
    if not script_choice:
        print("[ERROR] No script provided. Please try again.")
        return

    # Construct and execute the spawn command
    command = f"frida -U -f {package_name} -l {script_choice}"
    print(f"[INFO] Executing: {colorize(bold(command), 'cyan')}")

    # Use Popen to avoid blocking and provide continuous output
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("[INFO] App is being spawned. Output will be displayed below:\n")
        for line in process.stdout:
            print(line.strip())
        process.wait()
    except Exception as e:
        print(f"[ERROR] Failed to spawn the app: {e}")
def inject_app_with_pid():
    """Allow the user to select an app by PID and inject a script."""
    print("[INFO] Listing running processes on the emulator...")
    apps = list_running_apps(show_system_apps=False)
    
    if not apps:
        print("[ERROR] No processes found to inject.")
        return

    for idx, app in enumerate(apps, start=1):
        print(f"{bold(f'[{idx}] {app}')}")

    pid_input = input("\nEnter the PID of the process to inject: ").strip()
    if not pid_input.isdigit():
        print("[ERROR] Invalid PID. Please enter a valid number.")
        return

    # Prompt for script file or CodeShare URL
    script_choice = input("Enter the script file path or CodeShare URL: ").strip()
    if not script_choice:
        print("[ERROR] No script provided. Please try again.")
        return

    # Construct and execute the inject command
    command = f"frida -U -p {pid_input} -l {script_choice}"
    print(f"[INFO] Executing: {colorize(bold(command), 'cyan')}")

    # Use Popen to avoid blocking and provide continuous output
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("[INFO] Injecting script. Output will be displayed below:\n")
        for line in process.stdout:
            print(line.strip())
        process.wait()
    except Exception as e:
        print(f"[ERROR] Failed to inject the script: {e}")

def show_main_menu():
    """Display the main menu after setting up Frida."""
    while True:
        print("\nMain Menu:")
        print("[1] Start an app with a script from process (from script DB, file path, or CodeShare link).")
        print("[2] Inject an app with script using PID.")
        print("[3] Advanced Commands Menu (execute specific Frida commands).")
        print("[4] View available scripts (coming soon).")
        print("[5] Add a new script to the script DB (coming soon).")
        print("[6] Exit.")
        
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            spawn_app_with_script()
        elif choice == "2":
            inject_app_with_pid()
        elif choice == "3":
            show_advanced_menu()
        elif choice == "4":
            print("[INFO] This feature is not yet implemented. Stay tuned!")
        elif choice == "5":
            print("[INFO] This feature is not yet implemented. Stay tuned!")
        elif choice == "6":
            print("[INFO] Exiting. Goodbye!")
            exit()
        else:
            print("[ERROR] Invalid choice. Please try again.")

def show_advanced_menu():
    """Display advanced Frida commands and let the user select one."""
    while True:
        print("\nAdvanced Commands Menu:")
        print("[1] Start Frida session with an app (-U -f <package_name>).")
        print("[2] Attach to a running process by PID (-U -p <pid>).")
        print("[3] Load JavaScript while launching an app (-U -f <package_name> -l <script_path>).")
        print("[4] List all running processes (-Uia).")
        print("[5] Trace a function in an app (-U -i <function> -f <package_name>).")
        print("[6] Attach to an app and trace a function by PID (-U -p <pid> -i <function>).")
        print("[7] Discover all exported functions (-U -f <package_name>).")
        print("[8] Connect to a remote Frida server (-R <ip>:<port> -f <package_name>).")
        print("[9] Dump app memory (-U -f <package_name> -l dump_memory.js).")
        print("[10] Execute JavaScript directly on the app (-U -p <pid> -e <js_code>).")
        print("[11] Back to Main Menu.")
        
        choice = input("Enter your choice: ").strip()
        if choice == "11":
            return

        run_advanced_command(choice)

def run_advanced_command(choice):
    """Execute the selected advanced command."""
    if choice == "1":
        apps = list_running_apps()
        if not apps:
            return
        for idx, app in enumerate(apps, start=1):
            print(f"{bold(f'[{idx}] {app}')}")
        app_index = input("\nEnter the number corresponding to the app: ").strip()
        try:
            app_index = int(app_index)
            package_name = apps[app_index - 1].split()[-1]
        except (ValueError, IndexError):
            print("[ERROR] Invalid selection.")
            return
        command = f"frida -U -f {package_name}"
    elif choice == "2":
        apps = list_running_apps()
        if not apps:
            return
        for idx, app in enumerate(apps, start=1):
            print(f"{bold(f'[{idx}] {app}')}")
        pid = input("Enter the PID of the process to attach to: ").strip()
        if not pid.isdigit():
            print("[ERROR] Invalid PID.")
            return
        command = f"frida -U -p {pid}"
    elif choice == "3":
        apps = list_running_apps()
        if not apps:
            return
        for idx, app in enumerate(apps, start=1):
            print(f"{bold(f'[{idx}] {app}')}")
        app_index = input("\nEnter the number corresponding to the app: ").strip()
        try:
            app_index = int(app_index)
            package_name = apps[app_index - 1].split()[-1]
        except (ValueError, IndexError):
            print("[ERROR] Invalid selection.")
            return
        script_path = input("Enter the script file path: ").strip()
        command = f"frida -U -f {package_name} -l {script_path}"
    elif choice == "4":
        command = "frida-ps -Uia"
        print(f"[INFO] Executing: {colorize(bold(command), 'cyan')}")
        result = execute_command(command, shell=True)
        print(result if result else "[ERROR] Command failed or returned no output.")
    elif choice == "5":
        apps = list_running_apps()
        if not apps:
            return
        for idx, app in enumerate(apps, start=1):
            print(f"{bold(f'[{idx}] {app}')}")
        app_index = input("\nEnter the number corresponding to the app: ").strip()
        try:
            app_index = int(app_index)
            package_name = apps[app_index - 1].split()[-1]
        except (ValueError, IndexError):
            print("[ERROR] Invalid selection.")
            return
        function_name = input("Enter the function to trace (e.g., 'open'): ").strip()
        command = f"frida-trace -U -i \"{function_name}\" -f {package_name}"
        print(f"[INFO] Executing: {colorize(bold(command), 'cyan')}")
        result = execute_command(command, shell=True)
        print(result if result else "[ERROR] Command failed or returned no output.")
    elif choice == "6":
        apps = list_running_apps()
        if not apps:
            return
        for idx, app in enumerate(apps, start=1):
            print(f"{bold(f'[{idx}] {app}')}")
        pid = input("Enter the PID of the process to attach to: ").strip()
        if not pid.isdigit():
            print("[ERROR] Invalid PID.")
            return
        function_name = input("Enter the function to trace (e.g., 'open'): ").strip()
        command = f"frida-trace -U -p {pid} -i \"{function_name}\""
        print(f"[INFO] Executing: {colorize(bold(command), 'cyan')}")
        result = execute_command(command, shell=True)
        print(result if result else "[ERROR] Command failed or returned no output.")
    elif choice == "7":
        apps = list_running_apps()
        if not apps:
            return
        for idx, app in enumerate(apps, start=1):
            print(f"{bold(f'[{idx}] {app}')}")
        app_index = input("\nEnter the number corresponding to the app: ").strip()
        try:
            app_index = int(app_index)
            package_name = apps[app_index - 1].split()[-1]
        except (ValueError, IndexError):
            print("[ERROR] Invalid selection.")
            return
        command = f"frida-discover -U -f {package_name}"
        print(f"[INFO] Executing: {colorize(bold(command), 'cyan')}")
        result = execute_command(command, shell=True)
        print(result if result else "[ERROR] Command failed or returned no output.")
    elif choice == "8":
        ip = input("Enter the remote server IP: ").strip()
        port = input("Enter the remote server port (default: 27042): ").strip() or "27042"
        apps = list_running_apps()
        if not apps:
            return
        for idx, app in enumerate(apps, start=1):
            print(f"{bold(f'[{idx}] {app}')}")
        app_index = input("\nEnter the number corresponding to the app: ").strip()
        try:
            app_index = int(app_index)
            package_name = apps[app_index - 1].split()[-1]
        except (ValueError, IndexError):
            print("[ERROR] Invalid selection.")
            return
        command = f"frida -R {ip}:{port} -f {package_name}"
        print(f"[INFO] Executing: {colorize(bold(command), 'cyan')}")
        result = execute_command(command, shell=True)
        print(result if result else "[ERROR] Command failed or returned no output.")
    elif choice == "9":
        apps = list_running_apps()
        if not apps:
            return
        for idx, app in enumerate(apps, start=1):
            print(f"{bold(f'[{idx}] {app}')}")
        app_index = input("\nEnter the number corresponding to the app: ").strip()
        try:
            app_index = int(app_index)
            package_name = apps[app_index - 1].split()[-1]
        except (ValueError, IndexError):
            print("[ERROR] Invalid selection.")
            return
        command = f"frida -U -f {package_name} -l dump_memory.js"
        print(f"[INFO] Executing: {colorize(bold(command), 'cyan')}")
        result = execute_command(command, shell=True)
        print(result if result else "[ERROR] Command failed or returned no output.")
    elif choice == "10":
        apps = list_running_apps()
        if not apps:
            return
        for idx, app in enumerate(apps, start=1):
            print(f"{bold(f'[{idx}] {app}')}")
        pid = input("Enter the PID of the process to attach to: ").strip()
        if not pid.isdigit():
            print("[ERROR] Invalid PID.")
            return
        js_code = input("Enter the JavaScript code to execute: ").strip()
        command = f"frida -U -p {pid} -e \"{js_code}\""
        print(f"[INFO] Executing: {colorize(bold(command), 'cyan')}")
        result = execute_command(command, shell=True)
        print(result if result else "[ERROR] Command failed or returned no output.")
    else:
        print("[ERROR] Invalid choice. Please try again.")

def main():
    """Main function to coordinate the Frida setup and script execution."""
    print("[INFO] Welcome to the Frida Helper Script!")
    show_main_menu()

if __name__ == "__main__":
    main()
