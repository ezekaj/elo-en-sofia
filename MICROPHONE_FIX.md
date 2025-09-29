# 🎤 Microphone Access Fix Guide

## The Error You're Seeing

```
NotFoundError: Requested device not found
```

This means the browser cannot access your microphone, even though it exists.

## ✅ Quick Fix: Use Console Mode

**Console mode works perfectly** because it uses PyAudio directly (not browser API):

```bash
./run_console.sh
```

This is the **most reliable option** for macOS.

## 🔧 Fixing Browser Mode

### Option 1: Check Browser Permissions

1. **Open System Settings**
2. Go to **Privacy & Security** → **Microphone**
3. Enable your browser (Safari, Chrome, Firefox)
4. **Restart your browser completely**
5. Try `./run_dev.sh` again

### Option 2: Try Different Browser

Some browsers handle microphone access better than others:

1. **Chrome**: Usually best for WebRTC
2. **Safari**: Native macOS, often works well
3. **Firefox**: Good fallback option

### Option 3: Manual Gradio Access

1. Run `./run_dev.sh`
2. When browser opens, look for microphone permission prompt
3. Click "Allow" when prompted
4. Refresh page if needed

### Option 4: Check Browser Settings

**For Chrome**:
- chrome://settings/content/microphone
- Ensure site is not blocked

**For Safari**:
- Safari → Settings → Websites → Microphone
- Ensure http://127.0.0.1:7860 is allowed

**For Firefox**:
- about:preferences#privacy
- Permissions → Microphone → Settings

## 🎯 Recommended Solution

**Use Console Mode** - It's more reliable:

```bash
cd sofia-integrated
./run_console.sh
```

### Console Mode Advantages:
- ✅ Direct hardware access (no browser limitations)
- ✅ More reliable on macOS
- ✅ Lower latency
- ✅ No browser permission issues
- ✅ Works in pure terminal

### Console Mode Usage:
1. Run `./run_console.sh`
2. Wait for "🎤 Listening..."
3. Speak your message
4. Press Ctrl+C when done speaking
5. Sofia responds
6. Repeat or say "goodbye"

## 📊 System Check

Run this to verify your audio setup:

```bash
.venv/bin/python check_audio.py
```

This will show:
- ✅ Available microphones (PyAudio can see)
- ✅ Ollama status
- ✅ Models available

## 🐛 Why This Happens

The browser microphone API has stricter security than PyAudio:
- Browser needs explicit system permissions
- Browser needs HTTPS or localhost
- Some browsers cache permission denials
- macOS has additional security layers

## 💡 Summary

**Best Option**: Use console mode (`./run_console.sh`)
- Works immediately
- No permission issues
- More reliable on macOS

**Alternative**: Fix browser permissions and use dev mode
- Better UI
- Visual feedback
- Takes more setup