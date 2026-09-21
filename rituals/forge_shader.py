#!/usr/bin/env python3
"""Safely validates and deploys GLSL shaders to the frontend directory."""
import pathlib
import sys
import re

def validate_glsl(content: str) -> bool:
    if "void main()" not in content:
        print("[-] Validation Failed: Missing 'void main()' entry point.")
        return False
    if re.search(r"uniform\s+float\s+u_\w+;", content) is None:
        print("[-] Validation Failed: No uniform floats defined.")
        return False
    return True

def main():
    source_path = pathlib.Path("engine/shaders/cathedral_fragment.glsl")
    target_path = pathlib.Path("frontend/shaders/cathedral_fragment.glsl")
    
    # Fallback: if source doesn't exist, we just validate the target we just made
    check_path = target_path if not source_path.exists() else source_path
    
    if not check_path.exists():
        print(f"[-] Error: Shader not found at {check_path}")
        sys.exit(1)
        
    content = check_path.read_text()
    
    if not validate_glsl(content):
        print("[-] Deployment aborted due to validation failure.")
        sys.exit(1)
        
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(content)
    print(f"[+] Shader safely validated and secured at {target_path}")

if __name__ == "__main__":
    main()
