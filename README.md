# 🇮🇹 Beeper Desktop — Interfaccia in Italiano (UI Localization)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: macOS](https://img.shields.io/badge/Platform-macOS-lightgrey.svg)]()
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero%20(Pure%20Python%203)-success.svg)]()

Un patcher automatico e leggero per abilitare la **lingua italiana nell'interfaccia di Beeper Desktop** su macOS.

---

## 🧐 Il problema
Automattic e la community di Beeper hanno tradotto quasi l'intera app su **GlotPress** (la piattaforma di localizzazione di WordPress.com), tuttavia nel bundle JavaScript di Beeper Desktop (`app.asar`) la lista delle lingue attive nella UI è al momento ristretta a un gruppo limitato (`de`, `es`, `fr`, `ja`, `pt-BR`).

Anche impostando la lingua dell'app su **"System"** su un Mac in italiano, Beeper non trova l'italiano nella whitelist interna e forza il ripristino dell'interfaccia in inglese.

## 💡 La soluzione
Questo script (scritto in **puro Python 3, senza bisogno di Node, npm o asar**):
1. **Estrae in memoria** il bundle `app.asar` di Beeper Desktop.
2. **Inietta il dizionario ufficiale di traduzione** in italiano (estratto direttamente da GlotPress + rifiniture per le impostazioni e menu di Beeper).
3. **Abilita `it` nella whitelist** dei renderer (`nn`), rendendo selezionabile la voce **Italiano** in *Settings > General > App language*.
4. **Ricompila e firma** l'applicazione tramite `codesign` ad-hoc di macOS per prevenire crash all'avvio.
5. **Crea un backup automatico** (`app.asar.bak`) per permettere il ripristino in qualsiasi momento con un solo comando.

---

## 🚀 Installazione Rapida (One-Liner)

Apri il **Terminale** di macOS e incolla:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/PizzaRevolutions/beeper-desktop-italian/main/install.sh)
```

Al termine, riapri **Beeper Desktop**: l'app sarà direttamente in italiano e troverai la voce *Italiano* in **Impostazioni > Generale**.

---

## 🛠️ Installazione Manuale

Se preferisci clonare ed eseguire lo script manualmente:

```bash
# 1. Clona il repository
git clone https://github.com/PizzaRevolutions/beeper-desktop-italian.git
cd beeper-desktop-italian

# 2. Esegui il patcher
python3 patch.py
```

### Parametri opzionali:
- Se hai Beeper installato in una directory diversa:
  ```bash
  python3 patch.py --app-path "/percorso/personalizzato/Beeper Desktop.app"
  ```

---

## ↩️ Come disinstallare / Ripristinare l'originale

Se desideri rimuovere la patch e ripristinare il file originale di Beeper, puoi farlo in qualsiasi momento:

```bash
python3 patch.py --revert
```

Lo script ripristinerà istantaneamente il file `app.asar.bak` e rinnoverà la firma dell'app.

---

## 🛡️ Compatibilità e Sicurezza
- **Zero dipendenze esterne:** utilizza esclusivamente la libreria standard di Python 3 presente nativamente su macOS.
- **Supporto Apple Silicon & Intel:** compatibile con macOS Sonoma, Sequoia e versioni precedenti.
- **Nessuna modifica ai dati personali:** la patch tocca unicamente le risorse di visualizzazione dell'app (`app.asar`), senza modificare database di messaggi, credenziali o token.

---

## 🤝 Riconoscimenti & Licenza
- Progetto rilasciato con licenza [MIT](LICENSE).
- Traduzioni originali estratte dal progetto comunitario [Beeper Desktop su GlotPress](https://translate.wordpress.com/projects/beeper/desktop/it/default/) (Automattic / WordPress.com).
