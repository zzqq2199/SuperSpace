#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SIGNING_DIR="$PROJECT_DIR/.signing"
CERTIFICATE_NAME="${SPACEPP_SIGNING_IDENTITY:-SpacePP Local Self-Signed}"
CERTIFICATE_FILE="$SIGNING_DIR/spacepp-local-signing.crt"
PRIVATE_KEY_FILE="$SIGNING_DIR/spacepp-local-signing.key"
PKCS12_FILE="$SIGNING_DIR/spacepp-local-signing.p12"
PASSWORD_FILE="$SIGNING_DIR/spacepp-local-signing.password"
CONFIG_FILE="$SIGNING_DIR/spacepp-local-signing.conf"
LOGIN_KEYCHAIN="$HOME/Library/Keychains/login.keychain-db"

for command_name in openssl security; do
    if ! command -v "$command_name" >/dev/null 2>&1; then
        echo "Required command not found: $command_name" >&2
        exit 1
    fi
done

identity_exists() {
    security find-identity -v -p codesigning |
        awk -v identity="\"$CERTIFICATE_NAME\"" \
            'index($0, identity) { found = 1 } END { exit !found }'
}

mkdir -p "$SIGNING_DIR"
chmod 700 "$SIGNING_DIR"

if identity_exists; then
    security find-certificate -c "$CERTIFICATE_NAME" -p > "$CERTIFICATE_FILE"
    chmod 644 "$CERTIFICATE_FILE"
    echo "Code-signing identity already available: $CERTIFICATE_NAME"
    echo "Public certificate: $CERTIFICATE_FILE"
    exit 0
fi

cat > "$CONFIG_FILE" <<EOF
[ req ]
distinguished_name = req_name
prompt = no

[ req_name ]
CN = $CERTIFICATE_NAME

[ extensions ]
basicConstraints = critical,CA:false
keyUsage = critical,digitalSignature
extendedKeyUsage = critical,1.3.6.1.5.5.7.3.3
1.2.840.113635.100.6.1.14 = critical,DER:0500
EOF

password="$(openssl rand -base64 24)"
printf '%s\n' "$password" > "$PASSWORD_FILE"
chmod 600 "$PASSWORD_FILE"

echo "==> Generating a 10-year local code-signing certificate"
openssl genrsa -out "$PRIVATE_KEY_FILE" 2048
openssl req \
    -x509 \
    -new \
    -config "$CONFIG_FILE" \
    -key "$PRIVATE_KEY_FILE" \
    -extensions extensions \
    -sha256 \
    -days 3650 \
    -out "$CERTIFICATE_FILE"

pkcs12_compatibility_args=()
if [[ "$(openssl version)" == OpenSSL\ 3* ]]; then
    pkcs12_compatibility_args+=(-legacy)
fi

openssl pkcs12 "${pkcs12_compatibility_args[@]}" \
    -export \
    -inkey "$PRIVATE_KEY_FILE" \
    -in "$CERTIFICATE_FILE" \
    -out "$PKCS12_FILE" \
    -passout "pass:$password"

chmod 600 "$PRIVATE_KEY_FILE" "$PKCS12_FILE"
chmod 644 "$CERTIFICATE_FILE"

echo "==> Importing identity into the login keychain"
security import "$PKCS12_FILE" \
    -k "$LOGIN_KEYCHAIN" \
    -P "$password" \
    -T /usr/bin/codesign \
    -T /usr/bin/security

echo "==> Trusting the certificate for code signing on this Mac"
security add-trusted-cert \
    -r trustRoot \
    -p codeSign \
    -k "$LOGIN_KEYCHAIN" \
    "$CERTIFICATE_FILE"

if ! identity_exists; then
    echo "The new code-signing identity is not available in the keychain." >&2
    exit 1
fi

echo "==> Signing identity ready: $CERTIFICATE_NAME"
echo "    Private backup: $PKCS12_FILE"
echo "    Backup password: $PASSWORD_FILE"
echo "    Public certificate for other Macs: $CERTIFICATE_FILE"
