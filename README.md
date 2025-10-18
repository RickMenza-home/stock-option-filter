# 🐍 Building the Secured Put Option Finder App (Python → EXE)

This guide explains how to reinstall Python (for use in VS Code) and build a **standalone executable (.exe)** for the **Secured Put Option Finder** app, so that other users don’t need to install dependencies manually.

---

## 🧱 1. Install Python from the Official Website

1. Go to: [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)
2. Download the latest release (e.g. **Python 3.13.x**)
3. Run the installer and make sure to check both boxes:

   - ✅ **Add Python to PATH**
   - ✅ **Use admin privileges when installing py.exe**

4. Click **Install Now**

---

## 🧰 2. Verify the Installation

Open a **new VS Code terminal** (or Command Prompt) and run:

```bash
python --version
pip --version
```

You should see output similar to:
```bash
Python 3.13.1
pip 24.2 from C:\Users\<yourname>\AppData\...
```

---

## 📦 3. Install dependancies

Since the option chain API used is the Yahoo finance and need to create an installer file, install them with the following command:

```bash
pip install yfinance
pip install pyinstaller
```

Check installation:
```bash
pyinstaller --version
```

---

## 🏗️ 4. Build the Standalone Executable

From your project folder (where your Python script is saved), run:

```bash
pyinstaller --onefile --windowed your_script_name.py
```
Explanation:

--onefile → packages everything into a single .exe

--windowed → hides the console window (recommended for GUI apps)


After building, you’ll find your standalone app here:
```bash
dist/
 └── your_script_name.exe
```
You can share this .exe with other Windows users — they don’t need Python installed.