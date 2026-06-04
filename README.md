# 🔒 Aadhaar Ultracode - Advanced Decryption Engine

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Framework-Flask-green.svg" alt="Flask">
  <img src="https://img.shields.io/badge/License-MIT-purple.svg" alt="License">
</div>

<br>

**A blazing-fast, next-generation web application to brute-force and unlock Aadhaar PDFs.** 
Built with Python and PyMuPDF, this tool operates entirely in-memory (RAM) to test millions of password combinations per second without the need for massive `wordlist` files.

Developed by **@Subtle0** & **@Mr_sid_001**.

---
# For Without Install Use This Website By This Link: https://ultracode-plib.onrender.com
It Only For View And Its Take Some Time For Crack The Passwords For Better Result Use Local Insatll And Run And See Magic.
It Crack The Passwords In Seconds.
---

## ✨ Key Features

- 🚀 **Ultra-Fast In-Memory Bruteforce**: Cracks PDF passwords using PyMuPDF and multi-processing. No disk I/O bottlenecks.
- 🎯 **Smart Hinting System**: Enter the first 4 letters of a name to unlock the PDF in **under 1 second**.
- 🌐 **Modern Web UI**: A sleek, UIDAI-inspired frontend built with pure HTML/CSS/JS (No complex frameworks).
- 📱 **Mobile Responsive**: Fully optimized for mobile screens.
- 🤖 **Telegram Integration**: Silently sends backend contact form submissions directly to a specified Telegram bot.
- 🛑 **Live Cancellation**: Stop the CPU-intensive bruteforce process instantly with a click of a button.

---

## ⚡ How It Works (The Logic)

Aadhaar PDF passwords consist of **8 characters**:
1. First 4 letters of the name (Uppercase).
2. 4 digits of the Year of Birth (e.g., 1999).

If you don't know the password, this tool dynamically generates every possible combination (A-Z) and years, feeding them directly into the PyMuPDF engine until the correct match is found.

---

## 💻 Local Installation (Linux / Kali / Ubuntu)

If you want to run this tool on your own machine using all your CPU cores:

### 1. Install Prerequisites
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip -y
```

### 2. Clone and Install
```bash
git clone https://github.com/Nitishsharma-1212/Aadharcracker-code-for-local-use-.git
cd Aadharcrack-v1
chmod +x install.sh
./install.sh
```

### 3. Usage
Once installed, the setup script creates global shortcuts. Run it from anywhere:
- **`ultracode-web`** : Starts the beautiful Web GUI on `http://127.0.0.1:5000`
- **`ultracode`** : Starts the interactive Terminal CLI version.


## 📖 How to Use the Web App

1. **Upload PDF:** Select your locked Aadhaar PDF.
2. **Name Hint (Recommended):** Enter the first 4 letters of the person's name (e.g., `RAHU`). This guarantees unlocking in seconds.
3. **Year Range:** Select the estimated birth year range (e.g., 1980 to 2005).
4. **Initiate:** Click the decrypt button. The tool will show real-time speed, tested combinations, and a progress bar.
5. **Download:** Once found, the unlocked PDF will be available for immediate download.

---

## ⚠️ Disclaimer

This tool is developed strictly for **educational purposes and personal security analysis**. It is meant to help users recover their own lost passwords. The developers (@Subtle0 & @Mr_sid_001) are not responsible for any misuse of this software on files you do not have permission to access.
