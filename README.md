# Beeper Desktop — Interfaccia in Italiano

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: macOS | Windows | Linux](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey.svg)]()

Patcher per abilitare la lingua italiana nell'interfaccia di Beeper Desktop su macOS, Windows e Linux.

---

## Il problema
Beeper Desktop include traduzioni per diverse lingue, ma nel bundle JavaScript (`app.asar`) la lista delle lingue attive nella UI è limitata a sole 5 lingue (`de`, `es`, `fr`, `ja`, `pt-BR`).

Anche impostando la lingua del sistema operativo su italiano, Beeper non trova il locale nella whitelist interna e forza il ripristino dell'interfaccia in inglese.

## Funzionamento
Lo script (Python 3):
1. Rileva automaticamente la directory di installazione di Beeper su macOS, Windows e Linux.
2. Estrae il bundle `app.asar`.
3. Inietta il dizionario di traduzione in italiano (estratto da GlotPress con le chiavi d'interfaccia per impostazioni e menu).
4. Aggiunge `it` alla whitelist interna, rendendo selezionabile la voce **Italiano** in *Settings > General > App language*.
5. Ricompila il bundle e rinnova la firma ad-hoc con `codesign` (su macOS).
6. Crea un backup automatico (`app.asar.bak`) per consentire il ripristino.

---

## Installazione rapida

### macOS e Linux
Esegui nel terminale:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/PizzaRevolutions/beeper-desktop-italian/main/install.sh)
```

### Windows
Esegui in PowerShell:

```powershell
irm https://raw.githubusercontent.com/PizzaRevolutions/beeper-desktop-italian/main/install.ps1 | iex
```

Al termine, riavvia Beeper Desktop.

---

## Installazione manuale

```bash
# 1. Clona il repository
git clone https://github.com/PizzaRevolutions/beeper-desktop-italian.git
cd beeper-desktop-italian

# 2. Esegui il patcher
python3 patch.py    # su Windows: python patch.py
```

### Parametri opzionali
Se Beeper è installato in un percorso personalizzato:
```bash
python3 patch.py --app-path "/percorso/personalizzato/beeper"
```

---

## Disinstallazione

Per ripristinare il file originale dal backup:

```bash
python3 patch.py --revert
```

Lo script ripristina il file `app.asar.bak` e la firma originale.

---

## Note
- Utilizza esclusivamente la libreria standard di Python 3.
- Non modifica credenziali, token o cronologia messaggi: la modifica interessa unicamente le risorse grafiche dell'interfaccia (`app.asar`).

---

## Licenza
- Rilasciato sotto licenza [MIT](LICENSE).
- Traduzioni basate sul progetto comunitario [Beeper Desktop su GlotPress](https://translate.wordpress.com/projects/beeper/desktop/it/default/).
