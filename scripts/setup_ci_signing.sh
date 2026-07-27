#!/usr/bin/env bash
set -euo pipefail

CERTIFICATE_NAME="${SPACEPP_SIGNING_IDENTITY:-SpacePP Local Self-Signed}"
KEYCHAIN_PATH="${RUNNER_TEMP:-/tmp}/spacepp-signing.keychain-db"
KEYCHAIN_PASSWORD="$(openssl rand -base64 24)"
PKCS12_FILE="${RUNNER_TEMP:-/tmp}/spacepp-signing.p12"
CERTIFICATE_FILE="${RUNNER_TEMP:-/tmp}/spacepp-signing.crt"

if [[ -z "${SPACEPP_SIGNING_P12_BASE64:-}" ]]; then
    echo "Missing SPACEPP_SIGNING_P12_BASE64 secret." >&2
    exit 1
fi

if [[ -z "${SPACEPP_SIGNING_PASSWORD:-}" ]]; then
    echo "Missing SPACEPP_SIGNING_PASSWORD secret." >&2
    exit 1
fi

printf '%s' "$SPACEPP_SIGNING_P12_BASE64" | base64 -D > "$PKCS12_FILE"

security create-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN_PATH"
security set-keychain-settings -lut 21600 "$KEYCHAIN_PATH"
security unlock-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN_PATH"

security list-keychains -d user -s "$KEYCHAIN_PATH"

security import "$PKCS12_FILE" \
    -k "$KEYCHAIN_PATH" \
    -P "$SPACEPP_SIGNING_PASSWORD" \
    -T /usr/bin/codesign \
    -T /usr/bin/security

security set-key-partition-list \
    -S apple-tool:,apple: \
    -s \
    -k "$KEYCHAIN_PASSWORD" \
    "$KEYCHAIN_PATH" >/dev/null

security find-certificate \
    -c "$CERTIFICATE_NAME" \
    -p \
    "$KEYCHAIN_PATH" > "$CERTIFICATE_FILE"

sudo security add-trusted-cert \
    -d \
    -r trustRoot \
    -p codeSign \
    -k /Library/Keychains/System.keychain \
    "$CERTIFICATE_FILE"

if ! security find-identity -v -p codesigning "$KEYCHAIN_PATH" |
    awk -v identity="\"$CERTIFICATE_NAME\"" \
        'index($0, identity) { found = 1 } END { exit !found }'; then
    echo "Imported signing identity was not found: $CERTIFICATE_NAME" >&2
    exit 1
fi

echo "CI signing identity ready: $CERTIFICATE_NAME"
