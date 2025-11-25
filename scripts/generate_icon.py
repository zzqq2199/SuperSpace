import os
import subprocess
import shutil

def run(cmd):
    subprocess.run(cmd, check=True)

def convert_svg_to_png(svg_path, png_path, size):
    if shutil.which("rsvg-convert"):
        run(["rsvg-convert", "-w", str(size), "-h", str(size), "-o", png_path, svg_path])
    else:
        run(["sips", "-s", "format", "png", svg_path, "--out", png_path])
        run(["sips", "--resampleHeightWidth", str(size), str(size), png_path])

def generate_icns():
    iconset = "icons/SpacePP.iconset"
    os.makedirs(iconset, exist_ok=True)
    sizes = [128, 256, 512]
    for size in sizes:
        base = os.path.join(iconset, f"icon_{size}x{size}.png")
        convert_svg_to_png("icons/hyper_icon.svg", base, size)
        # @2x versions
        double = os.path.join(iconset, f"icon_{size}x{size}@2x.png")
        convert_svg_to_png("icons/hyper_icon.svg", double, size * 2)
    # Build icns
    run(["iconutil", "-c", "icns", "-o", "icons/spacepp.icns", iconset])

if __name__ == "__main__":
    generate_icns()
