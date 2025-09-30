# 🪟 Sofia Windows-Native Transformation Plan

## 🎯 Objective
Transform Sofia from Mac-centric WebRTC app to Windows-native voice AI assistant while preserving personality and functionality.

## ❌ What's Broken (Mac → Windows Issues)
1. **PyAudio** - Requires PortAudio C++ compilation
2. **webrtcvad** - Requires MSVC build tools
3. **fastrtc/aiortc** - Massive WebRTC stack (unnecessary for local app)
4. **80+ dependencies** - Installation nightmare (~2GB, 10-15 minutes)
5. **Bash scripts** - Don't work on Windows
6. **Unix paths** - Windows needs different handling

## ✅ New Windows-Native Architecture

### **Layer 1: Audio Capture**
- **Old:** PyAudio (C++ compilation needed)
- **New:** `sounddevice` (pure Python, pre-built Windows wheels)
- **Why:** No compilation, WASAPI backend for low latency

### **Layer 2: Voice Activity Detection (VAD)**
- **Old:** webrtcvad (C++ compilation)
- **New:** `webrtcvad-wheels` (already installed) OR `silero-vad` (neural)
- **Why:** Pre-built wheels, better accuracy

### **Layer 3: Speech-to-Text**
- **Old:** Moonshine via fastrtc (WebRTC complexity)
- **New:** `faster-whisper` (OpenAI Whisper, optimized)
- **Why:** Proven accuracy, Windows optimized, tiny.en model = fast
- **Performance:** 200-500ms transcription time

### **Layer 4: Large Language Model**
- **Keep:** Ollama with gemma3:4b
- **Why:** Already works perfectly on Windows
- **Status:** ✅ No changes needed

### **Layer 5: Text-to-Speech**
- **Keep:** Kokoro ONNX
- **Why:** Fast, high quality, ONNX runtime works great on Windows
- **Status:** ✅ No changes needed (but simplify dependencies)

### **Layer 6: User Interface**
- **Primary:** Gradio web UI (simplified)
- **Future:** Native Windows GUI with tkinter + system tray
- **Scripts:** Windows .bat files instead of bash

## 📦 New Dependency Stack (80% Reduction)

### Core Dependencies (~15 packages vs 80+)
```txt
# LLM
ollama>=0.4.7

# STT
faster-whisper>=0.10.0

# TTS
kokoro-onnx>=0.4.7

# Audio I/O
sounddevice>=0.4.6
numpy>=1.24.0

# VAD
webrtcvad-wheels>=2.0.14  # OR silero-vad

# UI
gradio>=4.0.0
fastapi>=0.100.0

# Utilities
loguru>=0.7.3
python-dotenv>=1.0.0
python-dateutil>=2.8.0

# Optional: Windows features
keyboard>=0.13.5  # For hotkeys
pystray>=0.19.4   # For system tray
```

### Installation Size Comparison
- **Old:** ~2GB, 80+ packages, 10-15 minutes
- **New:** ~500MB, 15 packages, 2-3 minutes

## 🏗️ New Project Structure

```
sofia-windows/
├── agent.py                    # Main entry point
├── setup-windows.bat           # Windows installer
├── run-gradio.bat             # Launch web UI
├── run-desktop.bat            # Launch native GUI (future)
├── requirements-windows.txt    # Minimal dependencies
├── config.json                # Windows-friendly settings
│
├── src/
│   ├── audio/                 # NEW: Windows-optimized audio
│   │   ├── capture.py        # sounddevice-based capture
│   │   ├── playback.py       # sounddevice-based playback
│   │   └── vad.py            # Voice activity detection
│   │
│   ├── stt/                   # NEW: Whisper engine
│   │   └── whisper_engine.py # faster-whisper wrapper
│   │
│   ├── tts/                   # MODIFIED: Simplified Kokoro
│   │   └── kokoro_engine.py  # Direct kokoro-onnx usage
│   │
│   ├── llm/                   # KEEP: Ollama client
│   │   └── ollama_client.py  # Keep as-is
│   │
│   ├── agent/                 # KEEP: Sofia's personality
│   │   ├── prompts.py        # ✅ No changes
│   │   ├── tools_local.py    # ✅ No changes
│   │   └── sofia_core.py     # ✅ Minimal changes
│   │
│   └── ui/                    # NEW: Windows UI options
│       ├── gradio_app.py     # Simplified web UI
│       └── desktop_app.py    # Native Windows GUI (future)
│
└── models/                    # Model cache directory
    └── .gitkeep
```

## 🚀 Implementation Phases

### Phase 1: Audio Layer Rewrite ⚡ CRITICAL
1. Create `src/audio/capture.py` using sounddevice
2. Create `src/audio/playback.py` using sounddevice
3. Create `src/audio/vad.py` with webrtcvad-wheels
4. Test audio round-trip (record → playback)

### Phase 2: STT Engine Replacement ⚡ CRITICAL
1. Create `src/stt/whisper_engine.py`
2. Use faster-whisper with tiny.en model
3. Implement streaming support
4. Benchmark vs Moonshine

### Phase 3: TTS Simplification ⚡ CRITICAL
1. Create `src/tts/kokoro_engine.py`
2. Use kokoro-onnx directly (bypass fastrtc)
3. Implement streaming synthesis
4. Test voice quality

### Phase 4: Sofia Core Integration ✅ PRESERVE
1. Copy Sofia's agent files unchanged
2. Update imports to new audio/stt/tts modules
3. Keep all personality and tools intact
4. Test conversation flow

### Phase 5: Windows Scripting 🪟
1. Create setup-windows.bat (installer)
2. Create run-gradio.bat (launcher)
3. Add prerequisites checker
4. Create desktop shortcut

### Phase 6: Gradio UI Simplification 🌐
1. Create simplified Gradio interface
2. Remove WebRTC dependencies
3. Add audio visualization
4. Add settings panel

### Phase 7: Testing & Optimization 🧪
1. End-to-end voice pipeline test
2. Performance benchmarking
3. Error handling and recovery
4. Windows 10/11 compatibility

### Phase 8: Windows-Native Features (Future) 🎨
1. System tray integration
2. Global hotkey support
3. Native Windows GUI
4. Windows notifications
5. Auto-start option

## ⚡ Performance Targets

| Metric | Target | Current (Mac) |
|--------|--------|---------------|
| Installation time | 2-3 min | 10-15 min |
| Dependencies | 15 packages | 80+ packages |
| Install size | 500MB | 2GB |
| STT latency | 200-500ms | 300-700ms |
| TTS latency | 100-200ms | 100-200ms |
| Memory usage | <1.5GB | ~2GB |
| CPU idle | <20% | ~30% |

## 🔧 Windows-Specific Optimizations

1. **WASAPI Audio Backend** - Low-latency audio via sounddevice
2. **Whisper CPU Optimization** - Use CTranslate2 with Intel MKL
3. **Model Caching** - Store in `%LOCALAPPDATA%/Sofia/models`
4. **Config Storage** - Use `%APPDATA%/Sofia/config.json`
5. **Path Handling** - Use pathlib for cross-path-separator compatibility
6. **COM Initialization** - Proper COM handling for audio devices

## 📋 Migration Checklist

- [ ] Create new branch `windows-native`
- [ ] Create minimal `requirements-windows.txt`
- [ ] Implement sounddevice audio capture
- [ ] Implement faster-whisper STT
- [ ] Simplify Kokoro TTS integration
- [ ] Port Sofia agent code (no changes)
- [ ] Create Windows .bat scripts
- [ ] Build simplified Gradio UI
- [ ] Test complete pipeline
- [ ] Document Windows setup
- [ ] Create installer script
- [ ] Benchmark performance
- [ ] Test on clean Windows 10/11 systems

## 🎯 Success Criteria

1. ✅ Installation works without MSVC/build tools
2. ✅ Complete install in under 5 minutes
3. ✅ Voice pipeline latency under 2 seconds
4. ✅ Sofia personality unchanged
5. ✅ All tools functional
6. ✅ Works on Windows 10 & 11
7. ✅ No bash scripts (all .bat)
8. ✅ Clean uninstall possible

## 🚨 What NOT to Change

- ✅ Sofia's personality (prompts.py)
- ✅ Sofia's tools (tools_local.py)
- ✅ Ollama integration
- ✅ Conversation management logic
- ✅ Sofia's name and identity

## 📈 Expected Outcomes

- **80% fewer dependencies** (15 vs 80+)
- **5x faster installation** (2-3 min vs 10-15 min)
- **75% smaller install** (500MB vs 2GB)
- **Same or better performance**
- **Better Windows integration**
- **Easier maintenance**
- **Happier Windows users** 🎉