#!/usr/bin/env python3
"""
Beeper Desktop Italian UI Patcher
Enables Italian (and community translations) as a selectable UI language in Beeper Desktop.
Zero dependencies — pure Python 3.
"""

import sys
import os
import re
import json
import struct
import shutil
import subprocess
import argparse
import urllib.request

APP_PATH_DEFAULT = "/Applications/Beeper Desktop.app"
INDEX_DB_PATH_DEFAULT = os.path.expanduser("~/Library/Application Support/BeeperTexts/index.db")
GLOTPRESS_URL = "https://translate.wordpress.com/projects/beeper/desktop/it/default/export-translations?format=jed1x"


def log(msg, symbol="ℹ️"):
    print(f"{symbol} {msg}")


def error(msg):
    print(f"❌ Errore: {msg}", file=sys.stderr)
    sys.exit(1)


def is_mac():
    return sys.platform == "darwin"


def close_beeper():
    log("Chiusura di Beeper Desktop in corso...")
    subprocess.run(["killall", "Beeper Desktop"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def remove_xattrs(app_path):
    if not is_mac():
        return
    for attr in ["com.apple.macl", "com.apple.provenance", "com.apple.quarantine"]:
        subprocess.run(["xattr", "-d", attr, app_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def unpack_asar(asar_bytes):
    _, total_size, size, json_size = struct.unpack("<IIII", asar_bytes[:16])
    header_json = asar_bytes[16:16 + json_size].decode("utf-8")
    header = json.loads(header_json)
    base_offset = 16 + json_size
    files = {}

    def extract_node(node, path=""):
        if "files" in node:
            for name, child in node["files"].items():
                extract_node(child, f"{path}/{name}" if path else name)
        elif node.get("unpacked"):
            pass
        elif "offset" in node:
            offset = int(node["offset"])
            fsize = int(node["size"])
            files[path] = asar_bytes[base_offset + offset : base_offset + offset + fsize]

    extract_node(header)
    return header, files


def pack_asar(header, files):
    payload = bytearray()

    def update_offsets(node, path=""):
        if "files" in node:
            for name, child in node["files"].items():
                update_offsets(child, f"{path}/{name}" if path else name)
        elif node.get("unpacked"):
            pass
        elif "offset" in node:
            content = files[path]
            offset = len(payload)
            node["offset"] = str(offset)
            node["size"] = len(content)
            payload.extend(content)

    update_offsets(header)
    json_str = json.dumps(header, separators=(",", ":"))
    json_bytes = json_str.encode("utf-8")
    pad_len = (4 - (len(json_bytes) % 4)) % 4
    json_bytes += b"\0" * pad_len

    json_size = len(json_bytes)
    u2 = json_size + 4
    u1 = u2 + 4
    u0 = 4

    out = bytearray()
    out.extend(struct.pack("<IIII", u0, u1, u2, json_size))
    out.extend(json_bytes)
    out.extend(payload)
    return bytes(out)


def load_translations(script_dir):
    local_file = os.path.join(script_dir, "translations", "it.json")
    if os.path.exists(local_file):
        try:
            with open(local_file, "r", encoding="utf-8") as f:
                log(f"Caricamento traduzioni dal file locale: {local_file}")
                return json.load(f)
        except Exception as e:
            log(f"Impossibile leggere file locale: {e}, provo con il download...", "⚠️")

    log("Scaricamento delle traduzioni ufficiali da GlotPress (WordPress.com)...")
    req = urllib.request.Request(GLOTPRESS_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        raw = json.loads(r.read().decode("utf-8"))
        messages = raw.get("locale_data", {}).get("messages", {})
        result = {
            "": {
                "domain": "beeper-desktop",
                "lang": "it",
                "plural-forms": "nplurals=2; plural=(n != 1);"
            }
        }
        for k, v in messages.items():
            if k and v and any(v):
                result[k] = v
        return result


def apply_patch(app_path, revert=False):
    res_dir = os.path.join(app_path, "Contents", "Resources")
    asar_path = os.path.join(res_dir, "app.asar")
    bak_path = os.path.join(res_dir, "app.asar.bak")

    if not os.path.exists(asar_path):
        error(f"app.asar non trovato in {asar_path}")

    close_beeper()
    remove_xattrs(app_path)

    if revert:
        if not os.path.exists(bak_path):
            error("Nessun backup (app.asar.bak) trovato da ripristinare.")
        log("Ripristino della versione originale di Beeper...")
        shutil.copy2(bak_path, asar_path)
        if is_mac():
            subprocess.run(["codesign", "--force", "--deep", "--sign", "-", app_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log("Ripristino completato con successo!", "✓")
        return

    # Backup se non esiste
    if not os.path.exists(bak_path):
        log(f"Creazione backup di sicurezza in: {bak_path}")
        shutil.copy2(asar_path, bak_path)

    log("Estrazione del pacchetto app.asar in memoria...")
    with open(bak_path, "rb") as f:
        asar_bytes = f.read()

    header, files = unpack_asar(asar_bytes)

    # Cerca il file bundle deep-link-*.js
    target_relpath = None
    for path in files:
        if path.startswith("build/renderer/deep-link-") and path.endswith(".js"):
            target_relpath = path
            break

    if not target_relpath:
        error("File deep-link-*.js non trovato all'interno di app.asar")

    log(f"File bundle individuato: {target_relpath}")
    js_content = files[target_relpath].decode("utf-8")

    # Verifica regex
    m_nn = re.search(r"nn=\[(\"de\",\"es\",\"fr\",\"ja\",\"pt-BR\")\]", js_content)
    if not m_nn:
        error("Whitelist delle lingue (nn) non trovata o già modificata.")

    m_bu = re.search(r"(Du=\{locale:[a-zA-Z0-9_$]+,localeData:[a-zA-Z0-9_$]+\},)(Bu=\{de:[a-zA-Z0-9_$]+,es:[a-zA-Z0-9_$]+,fr:[a-zA-Z0-9_$]+,ja:[a-zA-Z0-9_$]+,\"pt-BR\":[a-zA-Z0-9_$]+\};)", js_content)
    if not m_bu:
        error("Oggetto dizionari (Bu) non trovato.")

    # Carica traduzioni
    script_dir = os.path.dirname(os.path.abspath(__file__))
    it_dict = load_translations(script_dir)
    it_json = json.dumps(it_dict, separators=(",", ":"), ensure_ascii=False)
    escaped_json = it_json.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")

    # Inietta dizionario italiano e abilita "it"
    injection = f"{m_bu.group(1)}__it_data=JSON.parse(`{escaped_json}`),__it_obj={{locale:\"it\",localeData:__it_data}},"
    bu_patched = m_bu.group(2).replace("ja:", "it:__it_obj,ja:")
    full_bu_replacement = injection + bu_patched

    js_content = js_content.replace(m_bu.group(0), full_bu_replacement, 1)
    js_content = js_content.replace(m_nn.group(0), 'nn=["de","es","fr","it","ja","pt-BR"]', 1)

    files[target_relpath] = js_content.encode("utf-8")

    log("Ricompilazione del pacchetto app.asar...")
    new_asar_bytes = pack_asar(header, files)

    with open(asar_path, "wb") as f:
        f.write(new_asar_bytes)

    if is_mac():
        log("Rinnovo della firma ad-hoc su macOS con codesign...")
        subprocess.run(["codesign", "--force", "--deep", "--sign", "-", app_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Opzionale: imposta 'it' in index.db
    if os.path.exists(INDEX_DB_PATH_DEFAULT):
        try:
            import sqlite3
            conn = sqlite3.connect(INDEX_DB_PATH_DEFAULT)
            c = conn.cursor()
            row = c.execute("SELECT value FROM key_values WHERE key = 'localPrefs'").fetchone()
            if row:
                val = json.loads(row[0])
                val["app_locale"] = "it"
                c.execute("UPDATE key_values SET value = ? WHERE key = 'localPrefs'", (json.dumps(val),))
                conn.commit()
                log("Impostata la lingua predefinita su 'Italiano' nel database locale.")
        except Exception:
            pass

    log("Patch completata con successo!", "🎉")
    log("Ora puoi riaprire Beeper Desktop: l'italiano è attivo sia come lingua di sistema che nel selettore Impostazioni > Generale.")


def main():
    parser = argparse.ArgumentParser(description="Abilita l'italiano nell'interfaccia di Beeper Desktop.")
    parser.add_argument("--app-path", default=APP_PATH_DEFAULT, help="Percorso di Beeper Desktop.app (default: %(default)s)")
    parser.add_argument("--revert", action="store_true", help="Ripristina la versione originale di Beeper dal backup")
    args = parser.parse_args()

    apply_patch(args.app_path, revert=args.revert)


if __name__ == "__main__":
    main()
