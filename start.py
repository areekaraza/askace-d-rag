#!/usr/bin/env python3
"""
🚀 AskAce: D'RAG - Ultra-fast startup launcher
Optimized for minimal loading time and best performance
"""

import subprocess
import sys
from pathlib import Path


def setup_environment():
    """Quick environment setup"""
    # Create directories
    for directory in ['data', 'storage']:
        Path(directory).mkdir(exist_ok=True)
    print("📁 Environment ready")


def check_dependencies():
    """Fast dependency check"""
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__}")
        return True
    except ImportError:
        print("❌ Missing dependencies. Run: pip install -r requirements.txt")
        return False


def check_ollama():
    """Quick Ollama availability check"""
    try:
        import requests
        resp = requests.get("http://127.0.0.1:11434/api/tags", timeout=2)
        if resp.status_code == 200:
            models = resp.json().get("models", [])
            print(f"🤖 Ollama: {len(models)} models available")
        else:
            print("⚠️  Ollama running but no response")
    except:
        print("💡 Ollama not running - install from ollama.com")


def main():
    """Launch AskAce with optimized settings"""
    print("🎯 Starting AskAce: D'RAG...")
    
    setup_environment()
    
    if not check_dependencies():
        return 1
    
    check_ollama()
    
    print("🚀 Launching optimized interface...")
    
    # Launch with performance-optimized flags
    cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.headless", "true",
        "--server.fileWatcherType", "none",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false",
        "--browser.gatherUsageStats", "false",
        "--theme.base", "light"
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 AskAce stopped")
        return 0
    except Exception as e:
        print(f"❌ Launch failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())