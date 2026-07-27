#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_PATH="$PROJECT_DIR/dist/SpacePP.app"
SIGNING_IDENTITY="${SPACEPP_SIGNING_IDENTITY:-SpacePP Local Self-Signed}"
PUBLIC_CERTIFICATE="$PROJECT_DIR/dist/spacepp-local-signing.crt"
TRUST_SCRIPT="$PROJECT_DIR/dist/trust_signing_certificate.sh"
CLEAN_BUILD=false
OPEN_APP=false

usage() {
    cat <<'EOF'
Usage: ./scripts/build_app.sh [--clean] [--open]

  --clean  Clear PyInstaller caches before building
  --open   Open the app after a successful build
  --help   Show this help message
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --clean)
            CLEAN_BUILD=true
            ;;
        --open)
            OPEN_APP=true
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
    shift
done

if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "Space++ can only be packaged on macOS." >&2
    exit 1
fi

for command_name in uv codesign ditto plutil security; do
    if ! command -v "$command_name" >/dev/null 2>&1; then
        echo "Required command not found: $command_name" >&2
        exit 1
    fi
done

if ! security find-identity -v -p codesigning |
    awk -v identity="\"$SIGNING_IDENTITY\"" \
        'index($0, identity) { found = 1 } END { exit !found }'; then
    echo "Required code-signing identity not found: $SIGNING_IDENTITY" >&2
    echo "Run ./scripts/setup_local_signing.sh once, then build again." >&2
    exit 1
fi

cd "$PROJECT_DIR"

echo "==> Installing locked dependencies"
uv sync --locked --inexact

echo "==> Generating validated app icons"
uv run python scripts/generate_icon.py

build_args=(--noconfirm)
if [[ "$CLEAN_BUILD" == true ]]; then
    build_args+=(--clean)
fi

echo "==> Building SpacePP.app"
uv run pyinstaller "${build_args[@]}" SpacePP.spec

if [[ ! -d "$APP_PATH" ]]; then
    echo "Build completed without producing $APP_PATH" >&2
    exit 1
fi

for resource in \
    "$APP_PATH/Contents/Resources/config.json" \
    "$APP_PATH/Contents/Resources/SpacePP.icns"; do
    if [[ ! -f "$resource" ]]; then
        echo "Required app resource is missing: $resource" >&2
        exit 1
    fi
done

expected_version="$(uv run python -c 'from version import __version__; print(__version__)')"
bundle_version="$(plutil -extract CFBundleShortVersionString raw "$APP_PATH/Contents/Info.plist")"
if [[ "$bundle_version" != "$expected_version" ]]; then
    echo "Version mismatch: source=$expected_version bundle=$bundle_version" >&2
    exit 1
fi

echo "==> Signing with stable identity: $SIGNING_IDENTITY"
codesign \
    --force \
    --deep \
    --sign "$SIGNING_IDENTITY" \
    --timestamp=none \
    "$APP_PATH"
codesign --verify --deep --strict "$APP_PATH"
security find-certificate -c "$SIGNING_IDENTITY" -p > "$PUBLIC_CERTIFICATE"
cp "$PROJECT_DIR/scripts/trust_signing_certificate.sh" "$TRUST_SCRIPT"
chmod +x "$TRUST_SCRIPT"

package_name="SpacePP-$bundle_version-macos-$(uname -m)"
package_dir="$PROJECT_DIR/dist/$package_name"
package_zip="$PROJECT_DIR/dist/$package_name.zip"
rm -rf "$package_dir" "$package_zip"
mkdir -p "$package_dir"
ditto "$APP_PATH" "$package_dir/SpacePP.app"
cp "$PUBLIC_CERTIFICATE" "$TRUST_SCRIPT" "$package_dir/"
ditto -c -k --sequesterRsrc --keepParent "$package_dir" "$package_zip"

echo "==> Build ready: $APP_PATH (version $bundle_version)"
echo "    Public certificate: $PUBLIC_CERTIFICATE"
echo "    Trust helper for another Mac: $TRUST_SCRIPT"
echo "    Transfer package: $package_zip"
echo "    Open it with: open \"$APP_PATH\""

if [[ "$OPEN_APP" == true ]]; then
    open "$APP_PATH"
fi
