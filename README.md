# 🐍 PyOS v4.5.1

**PyOS** is a modular, terminal-based operating environment built with Python. Originally inspired by minimalist Unix shells.
---

## 🚀 Quick Start Guide

### 1. Prerequisites
PyOS requires **Python 3.8+** and **Tkinter**. Most systems have Python, but Tkinter might need a manual install:

* **Linux (Ubuntu/Debian):** `sudo apt install python3-tk python3-pip`
* **Linux (Arch):** `sudo pacman -S tk python-pip`
* **Linux (Fedora):** `sudo dnf install python3-tkinter`
* **macOS:** `brew install python-tk`
* **Windows:** Ensure "tcl/tk and IDLE" was checked during Python installation.

### 2. External Dependencies
Install the necessary libraries for the Serpent Browser and System Monitor:
```bash
pip install requests beautifulsoup4 psutil
```

### 3. Installation (Release Version)
1. Download `PyOS_release.zip` from the Releases section.
2. Extract the archive into a folder named `PyOS`.
3. Open your terminal in that folder and launch the system:
```bash
python3 pyos.py
