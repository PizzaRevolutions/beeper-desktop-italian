#!/usr/bin/env bash
set -e

echo "=============================================="
echo "🇮🇹  Beeper Desktop — Traduzione Italiana UI"
echo "=============================================="
echo ""

TMP_DIR=$(mktemp -d 2>/dev/null || mktemp -d -t 'beeper_it')
REPO_URL="https://github.com/PizzaRevolutions/beeper-desktop-italian.git"

cleanup() {
    rm -rf "$TMP_DIR"
}
trap cleanup EXIT

echo "⬇️  Download del patcher..."
git clone --depth 1 "$REPO_URL" "$TMP_DIR" > /dev/null 2>&1

echo "⚡ Esecuzione della patch..."
if command -v python3 >/dev/null 2>&1; then
    python3 "$TMP_DIR/patch.py" "$@"
elif command -v python >/dev/null 2>&1; then
    python "$TMP_DIR/patch.py" "$@"
else
    echo "❌ Errore: Python non trovato. Installa Python 3 per continuare."
    exit 1
fi

echo ""
echo "✨ Fatto! Riapri Beeper Desktop e goditi l'interfaccia in italiano."
