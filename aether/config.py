"""
config.py

Global configuration constants for the Aether assistant.
Resolves paths for llama-server.exe, the GGUF model files, and output logs.
"""

import os
from pathlib import Path

# Base workspace directory resolved dynamically
CURRENT_DIR = Path(__file__).parent.resolve()
WORKSPACE_ROOT = CURRENT_DIR.parent

def resolve_llama_server_path() -> Path:
    """
    Resolves the llama-server executable path dynamically without hardcoding.
    Checks environment variable, system PATH, workspace runtime/, and local config.
    """
    import shutil
    
    env_path = os.environ.get("LLAMA_SERVER_PATH")
    if env_path:
        return Path(env_path)

    bin_name = "llama-server.exe" if os.name == "nt" else "llama-server"
    platform_dir = "windows-x64" if os.name == "nt" else "mac-arm64"

    # Check system PATH (e.g. if installed globally)
    system_path = shutil.which(bin_name)
    if system_path:
        return Path(system_path)

    # Search local candidate layouts
    candidates = [
        WORKSPACE_ROOT / "runtime" / platform_dir / bin_name,
        WORKSPACE_ROOT / "aether-main" / "runtime" / platform_dir / bin_name,
        WORKSPACE_ROOT.parent / "aether-main" / "runtime" / platform_dir / bin_name,
        WORKSPACE_ROOT.parent.parent / "aether-main" / "runtime" / platform_dir / bin_name,
    ]

    for p in candidates:
        if p.exists():
            return p

    # Fallback to default nested directory structure
    return WORKSPACE_ROOT.parent.parent / "aether-main" / "runtime" / platform_dir / bin_name

# Dynamically resolve ATHER_DIR and LLAMA_SERVER_PATH
LLAMA_SERVER_PATH = resolve_llama_server_path()
ATHER_DIR = LLAMA_SERVER_PATH.parent.parent.parent.parent

# Router (3B) and Planner (7B) model configurations
from aether.models.manager import load_models_config, resolve_model_path
models_cfg = load_models_config()

ROUTER_MODEL_NAME = models_cfg["router_model"]
PLANNER_MODEL_NAME = models_cfg["planner_model"]

# Resolve model paths dynamically with fallback checks
ROUTER_MODEL_PATH = resolve_model_path(ROUTER_MODEL_NAME)
PLANNER_MODEL_PATH = resolve_model_path(PLANNER_MODEL_NAME)

# Backward compatibility constants
MODEL_NAME = ROUTER_MODEL_NAME
MODEL_PATH = ROUTER_MODEL_PATH
PORT = 12345

# Llama server connection details
HOST = "127.0.0.1"
ROUTER_PORT = 12345
PLANNER_PORT = 12346

ROUTER_BASE_URL = f"http://{HOST}:{ROUTER_PORT}"
PLANNER_BASE_URL = f"http://{HOST}:{PLANNER_PORT}"

# Backward compatibility URL
BASE_URL = ROUTER_BASE_URL

# Timeout for completion requests in seconds
# COMPLETION_TIMEOUT = 180.0
ROUTER_COMPLETION_TIMEOUT = 180.0
PLANNER_COMPLETION_TIMEOUT = 420.0
COMPLETION_TIMEOUT = ROUTER_COMPLETION_TIMEOUT
# Directory for logs
LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)
LOG_FILE = LOGS_DIR / "aether.log"

# Email summary configuration
MAX_SUMMARIZED_EMAILS = 10
SUMMARY_MAX_WORDS = 250

