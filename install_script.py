#!/usr/bin/env python3
"""
StrawberryFist VRAM Optimizer Installation Script
"""

import os
import sys
import subprocess
import importlib.util

def install_package(package_name):
    """Install a Python package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✅ Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_name}: {e}")
        return False

def check_package(package_name):
    """Check if a package is already installed"""
    spec = importlib.util.find_spec(package_name)
    return spec is not None

def main():
    print("🍓 StrawberryFist VRAM Optimizer Installation")
    print("=" * 50)
    
    # Required packages
    required_packages = [
        "GPUtil>=1.4.0",
    ]
    
    print("📋 Checking required packages...")
    
    for package in required_packages:
        package_name = package.split(">=")[0].split("==")[0]
        
        if check_package(package_name):
            print(f"✅ {package_name} is already installed")
        else:
            print(f"📦 Installing {package}...")
            if not install_package(package):
                print(f"❌ Installation failed for {package}")
                sys.exit(1)
    
    # Check PyTorch installation
    if check_package("torch"):
        print("✅ PyTorch is already installed")
        
        # Check CUDA availability
        try:
            import torch
            if torch.cuda.is_available():
                print(f"✅ CUDA is available (Device: {torch.cuda.get_device_name(0)})")
            else:
                print("⚠️  CUDA is not available - CPU mode will be used")
        except Exception as e:
            print(f"⚠️  Could not check CUDA status: {e}")
    else:
        print("⚠️  PyTorch not found - please install it according to your system requirements")
        print("   Visit: https://pytorch.org/get-started/locally/")
    
    print("\n🎉 Installation completed!")
    print("📝 Next steps:")
    print("1. Restart ComfyUI")
    print("2. Look for 'StFist - VRAM Optimizer' and 'StFist - GPU Monitor' nodes")
    print("3. Add them to your workflow and configure as needed")
    print("\n🍓 Thank you for using StrawberryFist VRAM Optimizer!")

if __name__ == "__main__":
    main()