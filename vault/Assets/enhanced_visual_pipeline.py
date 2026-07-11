#!/usr/bin/env python3
"""
Run enhanced_visual_pipeline.py to regenerate all visual assets
"""

import os
import sys
from pathlib import Path

VAULT_PATH = Path("/Users/ajadvanwyk/Downloads/Litigation Skills for South African Lawyers.pdf/vault")
ASSETS_PATH = VAULT_PATH / "Assets"

def check_dependencies():
    """Check that required Python packages are installed."""
    missing = []
    
    try:
        import matplotlib
    except ImportError:
        missing.append("matplotlib")
    
    try:
        import PIL
    except ImportError:
        missing.append("Pillow")
    
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print("Run: pip install " + " ".join(missing))
        return False
    return True

def generate_animations():
    """Run the animation generator."""
    print("\n========== GENERATING ANIMATIONS ==========")
    script_path = ASSETS_PATH / "litigation_animations.py"
    if script_path.exists():
        os.system(f"python3 '{script_path}'")
    else:
        print("Animation script not found")

def generate_mindmaps():
    """Run the mind map generator."""
    print("\n========== GENERATING MIND MAPS ==========")
    script_path = ASSETS_PATH / "generate_mindmaps.py"
    if script_path.exists():
        os.system(f"python3 '{script_path}'")
    else:
        print("Mind map script not found")

def main():
    print("SOUTH AFRICAN LITIGATION SKILLS")
    print("Visual Assets Pipeline v2.0")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Generate visuals
    generate_animations()
    generate_mindmaps()
    
    print("\n" + "=" * 60)
    print("VISUAL GENERATION COMPLETE")
    print("=" * 60)
    
    # List generated files
    print("\nGenerated Assets:")
    
    # SVGs
    svg_files = list(ASSETS_PATH.glob("*.svg"))
    for svg in svg_files:
        print(f"  SVG: {svg.name}")
    
    # Mind maps
    mindmap_path = ASSETS_PATH / "mindmaps"
    if mindmap_path.exists():
        html_files = list(mindmap_path.glob("*.html"))
        for html in html_files:
            print(f"  Mind Map: {html.name}")
    
    # GIFs
    gif_files = list(ASSETS_PATH.glob("*.gif"))
    for gif in gif_files:
        print(f"  Animation: {gif.name}")
    
    print("\nOpen the Dashboard.md to access all visuals!")

if __name__ == "__main__":
    main()
