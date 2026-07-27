import os
import subprocess
import shutil
import struct

def run(cmd):
    subprocess.run(cmd, check=True)

def convert_svg_to_png(svg_path, png_path, size):
    converter = shutil.which("rsvg-convert")
    if not converter:
        raise RuntimeError(
            "rsvg-convert is required for reliable icon rendering. "
            "Install it with: brew install librsvg"
        )
    run([converter, "-w", str(size), "-h", str(size), "-o", png_path, svg_path])

    with open(png_path, "rb") as png_file:
        header = png_file.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"Invalid PNG generated: {png_path}")
    width, height = struct.unpack(">II", header[16:24])
    if (width, height) != (size, size):
        raise RuntimeError(
            f"Invalid icon size for {png_path}: "
            f"expected {size}x{size}, got {width}x{height}"
        )

def generate_icns():
    iconset = "icons/SpacePP.iconset"
    shutil.rmtree(iconset, ignore_errors=True)
    os.makedirs(iconset, exist_ok=True)
    sizes = [16, 32, 128, 256, 512]
    for size in sizes:
        base = os.path.join(iconset, f"icon_{size}x{size}.png")
        convert_svg_to_png("icons/hyper_icon.svg", base, size)
        # @2x versions
        double = os.path.join(iconset, f"icon_{size}x{size}@2x.png")
        convert_svg_to_png("icons/hyper_icon.svg", double, size * 2)
    # Build icns
    run(["iconutil", "-c", "icns", "-o", "icons/SpacePP.icns", iconset])

if __name__ == "__main__":
    generate_icns()
