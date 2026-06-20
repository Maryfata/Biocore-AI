#!/usr/bin/env python3
"""Installation and verification script for BIOCORE AI dependencies."""

import sys
import subprocess
import os

def run_command(cmd, description):
    """Run a shell command and report results."""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    print(f"Running: {cmd}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0

def main():
    """Main installation routine."""
    
    print("\n" + "="*60)
    print("🚀 BIOCORE AI - DEPENDENCY INSTALLATION")
    print("="*60)
    
    # Step 1: Upgrade pip
    print("\n[1/5] Upgrading pip...")
    run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrade pip")
    
    # Step 2: Install core dependencies
    print("\n[2/5] Installing core dependencies...")
    core_deps = [
        "streamlit>=1.25.0",
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        "plotly>=5.0.0",
        "scikit-learn>=1.0.0",
        "Pillow>=8.0.0",
    ]
    
    for dep in core_deps:
        run_command(f"{sys.executable} -m pip install --upgrade {dep}", f"Install {dep}")
    
    # Step 3: Install MediaPipe (problematic - install separately)
    print("\n[3/5] Installing MediaPipe (separate step)...")
    run_command(f"{sys.executable} -m pip uninstall -y mediapipe", "Remove old mediapipe")
    run_command(f"{sys.executable} -m pip install --upgrade --force-reinstall mediapipe>=0.10.0", 
                "Install fresh mediapipe")
    
    # Step 4: Install speech/gesture dependencies
    print("\n[4/5] Installing voice & gesture dependencies...")
    gesture_deps = [
        "opencv-python>=4.8.0",
        "SpeechRecognition>=3.10.0",
        "pyaudio>=0.2.13",
    ]
    
    for dep in gesture_deps:
        run_command(f"{sys.executable} -m pip install --upgrade {dep}", f"Install {dep}")
    
    # Step 5: Install AI dependencies
    print("\n[5/5] Installing AI dependencies...")
    ai_deps = [
        "anthropic>=0.7.0",
        "shap>=0.42.0",
        "lime>=0.2.0",
    ]
    
    for dep in ai_deps:
        run_command(f"{sys.executable} -m pip install --upgrade {dep}", f"Install {dep}")
    
    # Verification
    print("\n" + "="*60)
    print("✅ VERIFICATION")
    print("="*60)
    
    packages_to_check = [
        ("streamlit", "st"),
        ("numpy", "np"),
        ("scipy", None),
        ("pandas", "pd"),
        ("matplotlib", "plt"),
        ("plotly", None),
        ("sklearn", None),
        ("PIL", "Image"),
        ("cv2", None),
        ("mediapipe", "mp"),
        ("speech_recognition", "sr"),
        ("anthropic", None),
    ]
    
    failed = []
    
    for package, alias in packages_to_check:
        try:
            if alias:
                exec(f"import {package} as {alias}")
            else:
                exec(f"import {package}")
            print(f"✅ {package:20} - OK")
        except ImportError as e:
            print(f"❌ {package:20} - FAILED: {e}")
            failed.append(package)
    
    print("\n" + "="*60)
    if failed:
        print(f"❌ {len(failed)} package(s) failed to import: {', '.join(failed)}")
        print("\nTrying individual fixes...")
        
        for pkg in failed:
            if pkg == "pyaudio":
                print("\n⚠️  PyAudio may need manual installation:")
                print("  On Windows: pip install pipwin; pipwin install pyaudio")
                print("  On macOS: brew install portaudio; pip install pyaudio")
                print("  On Linux: sudo apt-get install portaudio19-dev; pip install pyaudio")
            elif pkg == "mediapipe":
                print("\n⚠️  MediaPipe issues - trying with specific version...")
                run_command(f"{sys.executable} -m pip install mediapipe==0.10.0", "Install specific mediapipe version")
    else:
        print("✅ All packages installed and verified successfully!")
    
    print("\n" + "="*60)
    print("📝 NEXT STEPS:")
    print("="*60)
    print("1. Set ANTHROPIC_API_KEY (get free key from https://console.anthropic.com):")
    print("   $env:ANTHROPIC_API_KEY = 'sk-your-key'  # PowerShell")
    print("   set ANTHROPIC_API_KEY=sk-your-key       # CMD")
    print("\n2. Run the app:")
    print("   streamlit run app/main.py")
    print("\n3. Explore the new features:")
    print("   - 🤖 JARVIS Copilot tab")
    print("   - 🤲 Hands-Off Mode tab")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
