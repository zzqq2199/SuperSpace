#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: ./scripts/trust_signing_certificate.sh /path/to/spacepp-local-signing.crt" >&2
    exit 2
fi

CERTIFICATE_FILE="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
LOGIN_KEYCHAIN="$HOME/Library/Keychains/login.keychain-db"

if [[ "$(uname -s)" != "Darwin" ]]; then
    echo "This script can only run on macOS." >&2
    exit 1
fi

if [[ ! -f "$CERTIFICATE_FILE" ]]; then
    echo "Certificate not found: $CERTIFICATE_FILE" >&2
    exit 1
fi

security add-trusted-cert \
    -r trustRoot \
    -p codeSign \
    -k "$LOGIN_KEYCHAIN" \
    "$CERTIFICATE_FILE"

echo "Trusted code-signing certificate: $CERTIFICATE_FILE"
echo "You can now copy SpacePP.app to /Applications and open it."
