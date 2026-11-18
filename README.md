# 🇮🇹 Beeper Desktop — Interfaccia in Italiano (UI Localization)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: macOS | Windows | Linux](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey.svg)]()
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero%20(Pure%20Python%203)-success.svg)]()

Un patcher automatico, multipiattaforma e leggero per abilitare la **lingua italiana nell'interfaccia di Beeper Desktop** su **macOS, Windows e Linux**.

---

## 🧐 Il problema
Automattic e la community di Beeper hanno tradotto quasi l'intera app su **GlotPress** (la piattaforma di localizzazione di WordPress.com). Tuttavia, nel bundle JavaScript di Beeper Desktop (`app.asar`) la lista delle lingue attive nella UI è al momento ristretta a sole 5 lingue (`de`, `es`, `fr`, `ja`, `pt-BR`).

Anche impostando la lingua dell'app su **"System"** su un sistema operativo in italiano, Beeper non trova l'italiano nella whitelist interna e forza il ripristino dell'interfaccia in inglese.

## 💡 La soluzione
Questo script (scritto in **puro Python 3, senza bisogno di Node, npm o asar**):
1. **Rileva automaticamente** la directory di installazione di Beeper su macOS, Windows e Linux.
2. **Estrae in memoria** il bundle `app.asar`.
3. **Inietta il dizionario ufficiale di traduzione** in italiano (estratto direttamente da GlotPress + rifiniture per le impostazioni e i menu di Beeper).
4. **Abilita `it` nella whitelist** interna dei renderer, rendendo selezionabile la voce **Italiano** in *Settings > General > App language*.
5. **Ricompila il bundle** e rinnova la firma `codesign` ad-hoc (su macOS) per garantire un avvio privo di errori.
6. **Crea un backup automatico** (`app.asar.bak`) per permettere il ripristino istantaneo in qualsiasi momento.

---

## 🚀 Installazione Rapida (One-Liner)

### 🍏 macOS & 🐧 Linux
Apri il Terminale e incolla:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/PizzaRevolutions/beeper-desktop-italian/main/install.sh)
```

### 🪟 Windows
Apri **PowerShell** e incolla:

```powershell
irm https://raw.githubusercontent.com/PizzaRevolutions/beeper-desktop-italian/main/install.ps1 | iex
```

Al termine dell'esecuzione, riapri **Beeper Desktop**: l'interfaccia sarà direttamente in italiano e troverai la voce *Italiano* in **Impostazioni > Generale**.

---

## 🛠️ Installazione Manuale (Qualsiasi OS)

Se preferisci clonare ed eseguire lo script manualmente:

```bash
# 1. Clona il repository
git clone https://github.com/PizzaRevolutions/beeper-desktop-italian.git
cd beeper-desktop-italian

# 2. Esegui il patcher
python3 patch.py    # su Windows: python patch.py
```

### Parametri opzionali:
- Se hai Beeper installato in una directory non standard:
  ```bash
  python3 patch.py --app-path "/percorso/personalizzato/beeper"
  ```
  *(Su Linux se installato a livello di sistema in `/opt/Beeper`, potrebbe essere necessario eseguire con `sudo`).*

---

## ↩️ Come disinstallare / Ripristinare l'originale

Se desideri rimuovere la patch e ripristinare il file originale di Beeper:

```bash
python3 patch.py --revert
```

Lo script ripristinerà istantaneamente il file `app.asar.bak` e la firma originale.

---

## 🛡️ Compatibilità e Sicurezza
- **Zero dipendenze esterne:** utilizza esclusivamente la libreria standard di Python 3.
- **Multipiattaforma:** supporta macOS (Apple Silicon & Intel), Windows 10/11 e distribuzioni Linux (Deb, RPM, Arch, ecc.).
- **Nessuna modifica ai dati personali:** la patch tocca unicamente le risorse di visualizzazione dell'app (`app.asar`), senza modificare database di messaggi, credenziali o token.

---

## 🤝 Riconoscimenti & Licenza
- Progetto rilasciato con licenza [MIT](LICENSE).
- Traduzioni originali estratte dal progetto comunitario [Beeper Desktop su GlotPress](https://translate.wordpress.com/projects/beeper/desktop/it/default/) (Automattic / WordPress.com).
