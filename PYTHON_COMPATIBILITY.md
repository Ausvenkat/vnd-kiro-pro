# Python Compatibility Guide

## Issue: Python 3.14 Compatibility

The error you're seeing is due to **Python 3.14 being too new** for the current package ecosystem. Most packages haven't fully updated to support Python 3.14 yet.

### Solution: Use Python 3.11 or 3.12

---

## Option 1: Use System Python 3.12 (Recommended)

### Check Available Versions
```bash
python3.12 --version
```

If not installed:
```bash
brew install python@3.12
```

### Create Fresh Virtual Environment with Python 3.12
```bash
cd /Users/venkatesh/Documents/Venkat/kiro/vnd-kiro-pro

# Remove old venv
rm -rf venv

# Create new venv with Python 3.12
python3.12 -m venv venv

# Activate
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### Test
```bash
streamlit run app.py
```

---

## Option 2: Use Python 3.11

### Check Version
```bash
python3.11 --version
```

Install if needed:
```bash
brew install python@3.11
```

### Create Virtual Environment
```bash
cd /Users/venkatesh/Documents/Venkat/kiro/vnd-kiro-pro
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Option 3: Downgrade Python Locally for This Project

```bash
# Check what Python versions are installed
ls /opt/homebrew/bin/python*

# Use specific version
/opt/homebrew/bin/python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Why This Happens

1. **Python 3.14** is brand new (just released)
2. **Protobuf**, **Streamlit**, and other packages haven't updated their C extensions yet
3. **C extensions** (compiled modules) are incompatible between Python versions
4. The error: `Metaclasses with custom tp_new are not supported` means the compiled protobuf module was built for an older Python

---

## Updated requirements.txt

Your `requirements.txt` has been updated to use newer versions that are more compatible:

```
streamlit>=1.32.0          (Latest version, better compatibility)
pytest>=7.4.0              (Compatible with older Python versions)
hypothesis>=6.86.0         (Latest)
protobuf>=4.25.0           (Latest protobuf with better support)
```

---

## Quick Fix Steps

### 1. Delete Old Virtual Environment
```bash
rm -rf venv
```

### 2. Create New With Python 3.12
```bash
python3.12 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Verify
```bash
python --version          # Should show 3.12.x
streamlit run app.py      # Should work now
```

---

## Verify Setup Works

### Run Demo (No UI needed)
```bash
python3 demo.py
```

### Run Tests
```bash
pytest tests/test_core.py -v
```

### Run App (Opens web UI)
```bash
streamlit run app.py
```

---

## If You Still Have Issues

### Complete Fresh Start
```bash
cd /Users/venkatesh/Documents/Venkat/kiro/vnd-kiro-pro

# Remove everything
rm -rf venv

# Start completely fresh with Python 3.12
python3.12 -m venv venv
source venv/bin/activate

# Upgrade pip first
pip install --upgrade pip setuptools wheel

# Install packages
pip install streamlit pytest hypothesis

# Test
streamlit run app.py
```

### Check Environment
```bash
which python          # Should show .../venv/bin/python
python --version      # Should show 3.12.x
pip --version         # Should show venv's pip
which streamlit        # Should show .../venv/bin/streamlit
```

---

## Recommended Python Versions for This Project

| Version | Status | Recommendation |
|---------|--------|-----------------|
| 3.14 | ❌ Too new | Don't use yet |
| 3.13 | ⚠️ May have issues | Not tested |
| 3.12 | ✅ **Recommended** | **Use this** |
| 3.11 | ✅ Works | Good alternative |
| 3.10 | ✅ Works | Works but older |

---

## Summary

**Use Python 3.12** instead of 3.14:

```bash
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

This should resolve all compatibility issues immediately! ✅
