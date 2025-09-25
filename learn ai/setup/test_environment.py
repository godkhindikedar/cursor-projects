#!/usr/bin/env python3
"""
Environment Test Script

Run this script to verify your ADK learning environment is set up correctly.
"""

import sys
import importlib
import subprocess
from typing import Dict, List

def check_python_version() -> bool:
    """Check if Python version is 3.8 or higher."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Good!")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need 3.8+")
        return False

def check_package(package_name: str, import_name: str = None) -> bool:
    """Check if a package is installed and importable."""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"✅ {package_name} - Installed")
        return True
    except ImportError:
        print(f"❌ {package_name} - Not installed")
        return False

def check_gcloud() -> bool:
    """Check if gcloud is installed and configured."""
    try:
        result = subprocess.run(['gcloud', 'version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Google Cloud SDK - Installed")
            return True
        else:
            print("❌ Google Cloud SDK - Not working properly")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Google Cloud SDK - Not installed or not in PATH")
        return False

def main():
    """Run all environment checks."""
    print("🔍 Checking ADK Learning Environment")
    print("=" * 50)
    
    checks = []
    
    # Check Python version
    checks.append(check_python_version())
    
    # Check core packages
    packages_to_check = [
        ("jupyter", "jupyter"),
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("requests", "requests"),
        ("google-cloud-aiplatform", "google.cloud.aiplatform"),
        ("google-auth", "google.auth"),
        ("python-dotenv", "dotenv")
    ]
    
    for package_name, import_name in packages_to_check:
        checks.append(check_package(package_name, import_name))
    
    # Check Google Cloud SDK
    checks.append(check_gcloud())
    
    # Summary
    print("\n" + "=" * 50)
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print("🎉 All checks passed! Your environment is ready for ADK learning.")
        print("\n📚 Next steps:")
        print("1. Review the foundations/agentic_ai_concepts.md")
        print("2. Try running examples/01_hello_agent.py")
        print("3. Follow the setup/install_guide.md for ADK installation")
    else:
        print(f"⚠️  {total - passed} checks failed. Please install missing components.")
        print("\n🔧 Installation commands:")
        print("pip install -r requirements.txt")
        print("Follow setup/install_guide.md for complete setup")
    
    print(f"\n📊 Results: {passed}/{total} checks passed")

if __name__ == "__main__":
    main()
