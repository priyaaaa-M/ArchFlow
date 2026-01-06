# 📦 How to Package and Share the Project

## 🗜️ Creating the Zip File

### **Windows (PowerShell/CMD):**
```bash
# Navigate to the parent directory
cd d:\ls_hackathon\ttv

# Create zip file
Compress-Archive -Path "LS_Hackathon (2)\LS_Hackathon" -DestinationPath "SystemDesignGenerator.zip"

# Alternative using 7-Zip (if installed)
7z a -tzip SystemDesignGenerator.zip "LS_Hackathon (2)\LS_Hackathon\*"
```

### **Windows (File Explorer):**
1. Navigate to `d:\ls_hackathon\ttv\`
2. Right-click on `LS_Hackathon (2)\LS_Hackathon` folder
3. Select "Send to" → "Compressed (zipped) folder"
4. Rename to `SystemDesignGenerator.zip`

### **Mac/Linux:**
```bash
# Navigate to parent directory
cd /path/to/ttv

# Create zip file
zip -r SystemDesignGenerator.zip "LS_Hackathon (2)/LS_Hackathon"

# Exclude unnecessary files
zip -r SystemDesignGenerator.zip "LS_Hackathon (2)/LS_Hackathon" -x "*/output/*" "*/__pycache__/*" "*/node_modules/*"
```

---

## 📋 What Your Friend Will Get

### **Complete Package Contents:**
```
SystemDesignGenerator.zip
└── LS_Hackathon/
    ├── 📄 SETUP_GUIDE.md          # Complete setup instructions
    ├── 📄 requirements.txt        # All Python dependencies
    ├── 📄 .env                    # API key configuration template
    ├── 📄 start_system.py         # One-command startup
    ├── 📄 api.py                  # FastAPI backend
    ├── (No Python Streamlit frontend included in this branch)
    ├── 📁 services/               # Core AI pipeline
    ├── 📁 prompts/                # AI prompts
    ├── 📁 crawlers/               # Web scraping
    ├── 📁 cleaning/               # Text processing
    └── 📁 output/                 # Generated diagrams
```

---

## 🚀 Instructions for Your Friend

### **Step 1: Extract**
```bash
# Extract the zip file
# Navigate to extracted folder
cd LS_Hackathon
```

### **Step 2: Read Setup Guide**
```bash
# Open and follow SETUP_GUIDE.md
# It has complete step-by-step instructions
```

### **Step 3: Quick Start**
```bash
# Install dependencies
pip install -r requirements.txt

# Install Graphviz (Windows)
winget install graphviz

# Configure API key in .env file
# Get Gemini API key: https://makersuite.google.com/app/apikey

# Start the system
python start_system.py

# Access at: http://127.0.0.1:8501
```

---

## 📧 Message to Send with the Zip

**Subject:** 🛠️ System Design Generator - Complete Project Package

**Message:**
```
Hey! 👋

I've packaged the complete System Design Generator project for you. This is a fully working AI-powered system that creates professional architecture diagrams.

📦 **What's included:**
- Complete Python codebase
- FastAPI backend + Streamlit frontend with interactive canvas
- AI pipeline (Google search → scraping → AI analysis → PNG generation)
- Setup guide with step-by-step instructions
- All dependencies and configuration files

🚀 **Quick start:**
1. Extract the zip file
2. Open SETUP_GUIDE.md and follow the instructions
3. Install dependencies: `pip install -r requirements.txt`
4. Install Graphviz: `winget install graphviz` (Windows)
5. Get a free Gemini API key: https://makersuite.google.com/app/apikey
6. Add it to the .env file
7. Run: `python start_system.py`
8. Open: http://127.0.0.1:8501

⚡ **What it does:**
- Enter "Netflix Streaming Architecture" → Get professional PNG in 60 seconds
- Interactive canvas for editing diagrams
- Real AWS/GCP/Azure icons and smart clustering
- Complete API for integration

📚 **Documentation:**
- SETUP_GUIDE.md - Complete setup instructions
- SYSTEM_DOCUMENTATION.md - Technical details
- API docs at http://127.0.0.1:8000/docs when running

🎯 **Perfect for:**
- Hackathon demos
- System design interviews  
- Architecture documentation
- Client presentations

The setup guide has everything you need - should take about 5 minutes to get running!

Let me know if you need any help! 🚀

Built with ❤️ by Team Quirkless Code
```

---

## 🔧 Optional: Clean Before Zipping

### **Remove Unnecessary Files:**
```bash
# Navigate to project folder
cd "LS_Hackathon (2)\LS_Hackathon"

# Remove cache files (optional)
rmdir /s /q __pycache__
rmdir /s /q services\__pycache__
rmdir /s /q crawlers\__pycache__
rmdir /s /q cleaning\__pycache__

# Remove old output files (optional)
# del output\*.png
# del output\*.txt
```

---

## 📊 File Size Expectations

- **Complete project**: ~50-100 MB
- **Without output files**: ~10-20 MB  
- **Core code only**: ~5-10 MB

The zip should be small enough to email or share via cloud storage.

---

**Your friend will have everything they need to continue development immediately!** 🎉