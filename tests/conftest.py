import os
import pytest
import httpx
import subprocess
import time
import shutil

BASE_URL = os.getenv("TEST_BASE_URL", "http://127.0.0.1:8000")
FRONTEND_URL = os.getenv("TEST_FRONTEND_URL", "http://127.0.0.1:5173")

@pytest.fixture(scope="session", autouse=True)
def _start_backend():
    """Ensure backend (and optionally frontend) server is running for tests."""
    python = os.path.join('.venv', 'Scripts', 'python.exe')
    back = subprocess.Popen([python, '-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', '8000'])
    # Wait for backend health
    for _ in range(50):
        try:
            r = httpx.get(f"{BASE_URL}/api/health", timeout=1.0)
            if r.status_code == 200 and r.json().get("status") == "ok":
                break
        except Exception:
            pass
        time.sleep(0.2)
    else:
        back.terminate(); raise RuntimeError("Backend failed to start for tests")

    # Optionally start frontend if package.json exists and npm is available
    front = None
    try:
        if os.path.exists('package.json') and shutil.which('npm'):
            env = os.environ.copy(); env['BROWSER'] = 'none'
            front = subprocess.Popen(['npm', 'run', 'dev', '--', '--host', '127.0.0.1', '--port', '5173'], env=env)
            # Wait for frontend to respond, but don't fail suite if it doesn't
            for _ in range(50):
                try:
                    r = httpx.get(FRONTEND_URL, timeout=1.0)
                    if r.status_code in (200, 302):
                        break
                except Exception:
                    pass
                time.sleep(0.2)
    except Exception:
        # Frontend is optional for API tests
        pass

    yield

    try:
        if front is not None:
            front.terminate()
    except Exception:
        pass
    try:
        back.terminate()
    except Exception:
        pass

@pytest.fixture
async def client():
    async with httpx.AsyncClient() as c:
        yield c

@pytest.fixture
async def auth_token(client: httpx.AsyncClient) -> str:
    # Ensure default user exists (idempotent) via direct script recommended in setup
    try:
        await client.post(f"{BASE_URL}/api/auth/bootstrap")
    except Exception:
        pass
    data = {
        "username": "doctor@maueyecare.com",
        "password": "MauEyeCareAdmin@2024",
        "grant_type": "password",
    }
    resp = await client.post(f"{BASE_URL}/api/auth/login", data=data)
    resp.raise_for_status()
    return resp.json()["access_token"]
