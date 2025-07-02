#!/usr/bin/env python3
"""
Sofi AI Package Dependency Checker
Verifies all required packages are installed and compatible
"""

import sys
import subprocess
from typing import Dict, List, Tuple, Optional
import importlib
import importlib.metadata
import re

def read_requirements(file_path: str = "requirements.txt") -> List[str]:
    """Read requirements from requirements.txt file"""
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        requirements = []
        for line in lines:
            line = line.strip()
            # Skip comments and empty lines
            if line and not line.startswith('#'):
                requirements.append(line)
        
        return requirements
    except FileNotFoundError:
        print(f"❌ Requirements file '{file_path}' not found!")
        return []

def parse_requirement(req_string: str) -> Tuple[str, Optional[str]]:
    """Parse requirement string to get package name and version constraint"""
    # Handle different requirement formats
    for separator in ['>=', '<=', '==', '>', '<', '!=']:
        if separator in req_string:
            parts = req_string.split(separator)
            return parts[0].strip(), f"{separator}{parts[1].strip()}"
    
    # Handle special cases like Flask[async]
    if '[' in req_string:
        return req_string.split('[')[0].strip(), None
    
    return req_string.strip(), None

def check_package_installed(package_name: str, version_constraint: Optional[str] = None) -> Tuple[bool, str, str]:
    """Check if a package is installed and meets version requirements"""
    try:
        installed_version = importlib.metadata.version(package_name)
        
        if version_constraint:
            try:
                # Simple version comparison for basic constraints
                if version_constraint.startswith('>='):
                    required_version = version_constraint[2:].strip()
                    if compare_versions(installed_version, required_version) >= 0:
                        return True, installed_version, "✅ Compatible"
                    else:
                        return False, installed_version, f"❌ Version too old (need {version_constraint})"
                elif version_constraint.startswith('=='):
                    required_version = version_constraint[2:].strip()
                    if installed_version == required_version:
                        return True, installed_version, "✅ Compatible"
                    else:
                        return False, installed_version, f"❌ Version mismatch (need {version_constraint})"
                else:
                    return True, installed_version, f"✅ Installed (version check skipped for {version_constraint})"
            except Exception as e:
                return True, installed_version, f"⚠️ Version check failed: {str(e)}"
        else:
            return True, installed_version, "✅ Installed"
            
    except importlib.metadata.PackageNotFoundError:
        return False, "Not installed", "❌ Missing"

def compare_versions(version1: str, version2: str) -> int:
    """Compare two version strings. Returns: -1 if v1 < v2, 0 if equal, 1 if v1 > v2"""
    def version_tuple(v):
        return tuple(map(int, (v.split("."))))
    
    try:
        v1_tuple = version_tuple(version1)
        v2_tuple = version_tuple(version2)
        
        if v1_tuple < v2_tuple:
            return -1
        elif v1_tuple > v2_tuple:
            return 1
        else:
            return 0
    except:
        return 0  # If version parsing fails, assume compatible

def test_critical_imports() -> Dict[str, bool]:
    """Test importing critical packages to ensure they work"""
    critical_packages = {
        'flask': 'Flask',
        'supabase': 'supabase',
        'openai': 'openai',
        'telebot': 'pyTelegramBotAPI', 
        'telegram': 'python-telegram-bot',
        'cv2': 'opencv-python',
        'PIL': 'pillow',
        'pytesseract': 'pytesseract',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'requests': 'requests',
        'jwt': 'PyJWT',
        'dotenv': 'python-dotenv'
    }
    
    results = {}
    
    print("\n🧪 Testing Critical Package Imports:")
    print("=" * 50)
    
    for import_name, package_name in critical_packages.items():
        try:
            importlib.import_module(import_name)
            results[package_name] = True
            print(f"✅ {package_name}: Import successful")
        except ImportError as e:
            results[package_name] = False
            print(f"❌ {package_name}: Import failed - {str(e)}")
        except Exception as e:
            results[package_name] = False
            print(f"⚠️ {package_name}: Import error - {str(e)}")
    
    return results

def check_system_dependencies():
    """Check for system-level dependencies"""
    print("\n🔧 Checking System Dependencies:")
    print("=" * 50)
    
    # Check if Tesseract is installed (required for pytesseract)
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        print("✅ Tesseract OCR: Installed and accessible")
    except Exception as e:
        print(f"❌ Tesseract OCR: {str(e)}")
        print("   Install from: https://github.com/tesseract-ocr/tesseract")
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✅ Python: {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"⚠️ Python: {python_version.major}.{python_version.minor}.{python_version.micro} (Recommended: 3.8+)")

def check_specific_functionality():
    """Test specific functionality that might fail"""
    print("\n🎯 Testing Specific Functionality:")
    print("=" * 50)
    
    # Test Flask
    try:
        from flask import Flask
        app = Flask(__name__)
        print("✅ Flask: App creation successful")
    except Exception as e:
        print(f"❌ Flask: {str(e)}")
    
    # Test Supabase
    try:
        from supabase import create_client
        # Don't actually connect, just test import and function access
        print("✅ Supabase: Client creation function accessible")
    except Exception as e:
        print(f"❌ Supabase: {str(e)}")
    
    # Test OpenAI
    try:
        from openai import OpenAI
        print("✅ OpenAI: Client class accessible")
    except Exception as e:
        print(f"❌ OpenAI: {str(e)}")
    
    # Test Telegram Bot
    try:
        import telebot
        print("✅ Telegram Bot (pyTelegramBotAPI): Library accessible")
    except Exception as e:
        print(f"❌ Telegram Bot: {str(e)}")
    
    # Test Image Processing
    try:
        from PIL import Image
        import cv2
        print("✅ Image Processing: PIL and OpenCV accessible")
    except Exception as e:
        print(f"❌ Image Processing: {str(e)}")

def main():
    """Main dependency check function"""
    print("🔍 Sofi AI Dependency Checker")
    print("=" * 50)
    
    # Check Python version
    check_system_dependencies()
    
    # Read requirements
    requirements = read_requirements()
    if not requirements:
        print("❌ No requirements found to check!")
        return False
    
    print(f"\n📦 Checking {len(requirements)} Package Requirements:")
    print("=" * 50)
    
    all_satisfied = True
    missing_packages = []
    version_issues = []
    
    for req in requirements:
        package_name, version_constraint = parse_requirement(req)
        is_installed, version, status = check_package_installed(package_name, version_constraint)
        
        print(f"{status} {package_name}: {version}")
        
        if not is_installed:
            all_satisfied = False
            missing_packages.append(package_name)
        elif "mismatch" in status.lower():
            version_issues.append(f"{package_name}{version_constraint}")
    
    # Test imports
    import_results = test_critical_imports()
    
    # Test specific functionality
    check_specific_functionality()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DEPENDENCY CHECK SUMMARY")
    print("=" * 50)
    
    if all_satisfied and all(import_results.values()):
        print("🎉 ALL DEPENDENCIES SATISFIED!")
        print("✅ All required packages are installed and working")
        print("🚀 Your Sofi AI application is ready to run!")
        return True
    else:
        print("⚠️ DEPENDENCY ISSUES FOUND:")
        
        if missing_packages:
            print(f"\n❌ Missing Packages ({len(missing_packages)}):")
            for pkg in missing_packages:
                print(f"   • {pkg}")
            print("\n🔧 Install missing packages:")
            print("   pip install " + " ".join(missing_packages))
        
        if version_issues:
            print(f"\n⚠️ Version Issues ({len(version_issues)}):")
            for pkg in version_issues:
                print(f"   • {pkg}")
            print("\n🔧 Update packages:")
            print("   pip install --upgrade " + " ".join([p.split('>=')[0].split('==')[0] for p in version_issues]))
        
        failed_imports = [pkg for pkg, success in import_results.items() if not success]
        if failed_imports:
            print(f"\n❌ Import Failures ({len(failed_imports)}):")
            for pkg in failed_imports:
                print(f"   • {pkg}")
        
        print("\n🔧 Quick Fix:")
        print("   pip install -r requirements.txt --upgrade")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
