#!/usr/bin/env bash
set -e

# Check root
if [[ "$EUID" -ne 0 ]]; then
  echo "❌ Please run as root or use sudo"
  exit 1
fi

# Detect bin directory
if [[ -d "/opt/homebrew/bin" ]]; then
  BIN_DIR="/opt/homebrew/bin"
else
  BIN_DIR="/usr/local/bin"
fi

# Check curl
command -v curl >/dev/null 2>&1 || {
  echo "❌ curl is not installed"
  exit 1
}

# Check php
command -v php >/dev/null 2>&1 || {
  echo "❌ PHP is not installed"
  exit 1
}

echo "📦 Installing WP-CLI to $BIN_DIR"

curl -L -o wp-cli.phar https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar

install -m 755 wp-cli.phar "$BIN_DIR/wp"

rm wp-cli.phar

echo "✅ WP-CLI installed successfully"
echo "👉 Try: wp --info"
