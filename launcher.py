import os
import sys
import subprocess


def get_base_dir() -> str:
    if getattr(sys, 'frozen', False):
        # Running as a PyInstaller bundle
        return os.path.dirname(sys.executable)
    # Running from source
    return os.path.dirname(os.path.abspath(__file__))


def main() -> int:
    base = get_base_dir()
    run_ps1 = os.path.join(base, 'run.ps1')

    if not os.path.exists(run_ps1):
        print('[MauEyeCare] run.ps1 not found next to the launcher. Ensure the launcher.exe is placed in the project root with run.ps1.')
        return 1

    # Invoke PowerShell run.ps1 in a new process
    try:
        cmd = [
            'powershell',
            '-NoProfile',
            '-ExecutionPolicy', 'Bypass',
            '-File', run_ps1
        ]
        # Use a separate process to keep the PowerShell window interactive
        completed = subprocess.run(cmd)
        return completed.returncode
    except FileNotFoundError:
        print('[MauEyeCare] PowerShell not found. Please run run.ps1 manually.')
        return 1
    except Exception as e:
        print(f"[MauEyeCare] Failed to start: {e}")
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
