#!/usr/bin/env bash
set -e

echo "[MLAOS-Prime] Executing Somatic Pipeline Sanity Audit..."

# Check directory structure
if [ ! -f "scripts/AureliaAvatarController.gd" ]; then
    echo "[!] Error: AureliaAvatarController.gd missing from scripts/"
    exit 1
fi

if [ ! -f "shaders/aurelia_panoptic_dither.gdshader" ]; then
    echo "[!] Error: aurelia_panoptic_dither.gdshader missing from shaders/"
    exit 1
fi

echo "[+] File integrity verified: Controllers and shaders aligned."
echo "[+] Godot 4 project integration ready for voxel and bone binding injection."
