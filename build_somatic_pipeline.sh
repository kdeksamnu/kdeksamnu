#!/usr/bin/env bash
set -e

echo "[MLAOS-Prime] Deploying Avatar Engine Binding: 12-Layer Somatic Stack..."

# Ensure target directories exist
mkdir -p scripts/ shaders/

# Move generated files into position if they exist in the root workspace
if [ -f "AureliaAvatarController.gd" ]; then
    mv AureliaAvatarController.gd scripts/
    echo "[+] AureliaAvatarController.gd placed into scripts/"
fi

if [ -f "aurelia_panoptic_dither.gdshader" ]; then
    mv aurelia_panoptic_dither.gdshader shaders/
    echo "[+] aurelia_panoptic_dither.gdshader placed into shaders/"
fi

echo "[MLAOS-Prime] Somatic Stack pipeline deployment complete. Ready for Godot 4 compilation."
