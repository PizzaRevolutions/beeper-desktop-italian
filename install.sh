#!/usr/bin/env bash
set -e

echo "=============================================="
echo "🇮🇹  Beeper Desktop — Traduzione Italiana UI"
echo "=============================================="
echo ""

TMP_DIR=$(mktemp -d)
REPO_URL="https://github.com/PizzaRevolutions/beeper-desktop-italian.git"

cleanup() {
    rm -rf "$TMP_DIR"
}
trap cleanup EXIT

echo "⬇️  Download del patcher..."
git clone --depth 1 "$REPO_URL" "$TMP_DIR" > /dev/null 2>&1

echo "⚡ Esecuzione della patch..."
python3 "$TMP_DIR/patch.py" "$@"

echo ""
echo "✨ Fatto! Riapri Beeper Desktop e goditi l'interfaccia in italiano."
