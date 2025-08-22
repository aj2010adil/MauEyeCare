import os
import sys
import subprocess
import time
import webbrowser
import http.client


def get_base_dir() -> str:
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def wait_health(url: str, timeout: float = 15.0) -> bool:
    end = time.time() + timeout
    parsed = url.replace('http://', '').split('/')
    host_port = parsed[0]
    path = '/' + '/'.join(parsed[1:]) if len(parsed) > 1 else '/'
    if ':' in host_port:
        host, port = host_port.split(':', 1)
        port = int(port)
    else:
        host, port = host_port, 80
    while time.time() < end:
        try:
            conn = http.client.HTTPConnection(host, port, timeout=1)
            conn.request('GET', path)
            resp = conn.getresponse()
            if resp.status == 200:
                return True
        except Exception:
            time.sleep(0.2)
        finally:
            try:
                conn.close()
            except Exception:
                pass
    return False


def main() -> int:
    base = get_base_dir()
    venv_python = os.path.join(base, '.venv', 'Scripts', 'python.exe')
    if not os.path.exists(venv_python):
        print('[MauEyeCare] .venv not found. Run setup.ps1 first.')
        return 1

    # Start backend
    try:
        backend = subprocess.Popen([
            venv_python,
            '-m', 'uvicorn',
            'main:app',
            '--host', '127.0.0.1',
            '--port', '8000'
        ], cwd=base)
    except Exception as e:
        print(f"[MauEyeCare] Failed to start backend: {e}")
        return 1

    # Wait for health
    if wait_health('http://127.0.0.1:8000/api/health', timeout=20):
        # Open frontend if available, else open API docs
        web_url = 'http://127.0.0.1:5173'
        try:
            if wait_health(web_url, timeout=2):
                webbrowser.open(web_url)
            else:
                webbrowser.open('http://127.0.0.1:8000/docs')
        except Exception:
            pass
    else:
        print('[MauEyeCare] Backend health check failed.')
        try:
            backend.terminate()
        except Exception:
            pass
        return 1

    # Keep launcher running until backend exits
    try:
        backend.wait()
    except KeyboardInterrupt:
        try:
            backend.terminate()
        except Exception:
            pass
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
