#!/usr/bin/env python3
"""
Beeper Desktop Italian UI Patcher
Enables Italian (and community translations) as a selectable UI language in Beeper Desktop.
Supports macOS, Windows, and Linux.
Zero external dependencies — pure Python 3.
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
import platform

GLOTPRESS_URL = "https://translate.wordpress.com/projects/beeper/desktop/it/default/export-translations?format=jed1x"


def log(msg, symbol="ℹ️"):
    print(f"{symbol} {msg}")


def error(msg):
    print(f"❌ Errore: {msg}", file=sys.stderr)
    sys.exit(1)


def get_platform():
    plat = platform.system().lower()
    if "darwin" in plat:
        return "mac"
    elif "windows" in plat:
        return "windows"
    else:
        return "linux"


def close_beeper():
    log("Chiusura di Beeper Desktop in corso...")
    plat = get_platform()
    if plat == "mac":
        subprocess.run(["killall", "Beeper Desktop"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif plat == "windows":
        subprocess.run(["taskkill", "/F", "/IM", "Beeper.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["taskkill", "/F", "/IM", "Beeper Desktop.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.run(["killall", "beeper"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["killall", "Beeper Desktop"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["pkill", "-f", "beeper"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def remove_xattrs(path):
    if get_platform() != "mac":
        return
    for attr in ["com.apple.macl", "com.apple.provenance", "com.apple.quarantine"]:
        subprocess.run(["xattr", "-d", attr, path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def find_asar_path(custom_path=None):
    if custom_path:
        custom_path = os.path.expanduser(custom_path)
        if os.path.isfile(custom_path) and custom_path.endswith(".asar"):
            return custom_path
        candidates = [
            os.path.join(custom_path, "Contents", "Resources", "app.asar"),
            os.path.join(custom_path, "resources", "app.asar"),
            os.path.join(custom_path, "app.asar"),
        ]
        for c in candidates:
            if os.path.isfile(c):
                return c
        return None

    plat = get_platform()
    candidates = []

    if plat == "mac":
        candidates = [
            "/Applications/Beeper Desktop.app/Contents/Resources/app.asar",
            os.path.expanduser("~/Applications/Beeper Desktop.app/Contents/Resources/app.asar"),
        ]
    elif plat == "windows":
        local_app_data = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
        prog_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        prog_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
        candidates = [
            os.path.join(local_app_data, "Programs", "Beeper", "resources", "app.asar"),
            os.path.join(local_app_data, "Programs", "Beeper Desktop", "resources", "app.asar"),
            os.path.join(local_app_data, "Beeper", "resources", "app.asar"),
            os.path.join(local_app_data, "BeeperTexts", "resources", "app.asar"),
            os.path.join(prog_files, "Beeper", "resources", "app.asar"),
            os.path.join(prog_files, "Beeper Desktop", "resources", "app.asar"),
            os.path.join(prog_files_x86, "Beeper", "resources", "app.asar"),
        ]
    else:  # Linux
        candidates = [
            "/opt/Beeper/resources/app.asar",
            "/opt/Beeper Desktop/resources/app.asar",
            "/opt/BeeperTexts/resources/app.asar",
            "/usr/lib/beeper/resources/app.asar",
            "/usr/share/beeper/resources/app.asar",
            os.path.expanduser("~/.local/share/beeper/resources/app.asar"),
            os.path.expanduser("~/squashfs-root/resources/app.asar"),
        ]

    for c in candidates:
        if os.path.isfile(c):
            return c

    return None


def find_index_db_path():
    plat = get_platform()
    if plat == "mac":
        path = os.path.expanduser("~/Library/Application Support/BeeperTexts/index.db")
    elif plat == "windows":
        app_data = os.environ.get("APPDATA", os.path.expanduser("~\\AppData\\Roaming"))
        path = os.path.join(app_data, "BeeperTexts", "index.db")
    else:
        xdg_config = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
        path = os.path.join(xdg_config, "BeeperTexts", "index.db")

    return path if os.path.isfile(path) else None


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


def apply_patch(custom_path=None, revert=False):
    asar_path = find_asar_path(custom_path)
    if not asar_path:
        error(
            "Impossibile trovare app.asar di Beeper Desktop nel sistema.\n"
            "Specifica il percorso manualmente con: --app-path /percorso/beeper"
        )

    log(f"File app.asar individuato: {asar_path}")
    res_dir = os.path.dirname(asar_path)
    bak_path = os.path.join(res_dir, "app.asar.bak")

    close_beeper()

    # Rimuovi xattr su macOS
    if get_platform() == "mac":
        app_bundle = asar_path
        while app_bundle and not app_bundle.endswith(".app"):
            parent = os.path.dirname(app_bundle)
            if parent == app_bundle:
                app_bundle = None
                break
            app_bundle = parent
        if app_bundle:
            remove_xattrs(app_bundle)

    if revert:
        if not os.path.exists(bak_path):
            error("Nessun backup (app.asar.bak) trovato da ripristinare.")
        log("Ripristino della versione originale di Beeper...")
        shutil.copy2(bak_path, asar_path)
        if get_platform() == "mac" and app_bundle:
            subprocess.run(["codesign", "--force", "--deep", "--sign", "-", app_bundle], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log("Ripristino completato con successo!", "✓")
        return

    # Crea backup se non esiste
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

    m_nn = re.search(r"nn=\[(\"de\",\"es\",\"fr\",\"ja\",\"pt-BR\")\]", js_content)
    if not m_nn:
        error("Whitelist delle lingue (nn) non trovata o già modificata.")

    m_bu = re.search(r"(Du=\{locale:[a-zA-Z0-9_$]+,localeData:[a-zA-Z0-9_$]+\},)(Bu=\{de:[a-zA-Z0-9_$]+,es:[a-zA-Z0-9_$]+,fr:[a-zA-Z0-9_$]+,ja:[a-zA-Z0-9_$]+,\"pt-BR\":[a-zA-Z0-9_$]+\};)", js_content)
    if not m_bu:
        error("Oggetto dizionari (Bu) non trovato.")

    # Carica dizionario
    script_dir = os.path.dirname(os.path.abspath(__file__))
    it_dict = load_translations(script_dir)
    it_json = json.dumps(it_dict, separators=(",", ":"), ensure_ascii=False)
    escaped_json = it_json.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")

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

    if get_platform() == "mac" and app_bundle:
        log("Rinnovo della firma ad-hoc su macOS con codesign...")
        subprocess.run(["codesign", "--force", "--deep", "--sign", "-", app_bundle], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Opzionale: imposta 'it' in index.db
    db_path = find_index_db_path()
    if db_path and os.path.exists(db_path):
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            row = c.execute("SELECT value FROM key_values WHERE key = 'localPrefs'").fetchone()
            if row:
                val = json.loads(row[0])
                val["app_locale"] = "it"
                c.execute("UPDATE key_values SET value = ? WHERE key = 'localPrefs'", (json.dumps(val),))
                conn.commit()
                log(f"Impostata la lingua predefinita su 'Italiano' nel database locale ({db_path}).")
        except Exception:
            pass

    log("Patch completata con successo!", "🎉")
    log("Ora puoi riaprire Beeper Desktop: l'italiano è attivo sia come lingua di sistema che nel selettore Impostazioni > Generale.")


def main():
    parser = argparse.ArgumentParser(description="Abilita l'italiano nell'interfaccia di Beeper Desktop (macOS, Windows, Linux).")
    parser.add_argument("--app-path", default=None, help="Percorso personalizzato dell'app o di app.asar")
    parser.add_argument("--revert", action="store_true", help="Ripristina la versione originale di Beeper dal backup")
    args = parser.parse_args()

    apply_patch(custom_path=args.app_path, revert=args.revert)


if __name__ == "__main__":
    main()
