# Sofia Integrated - Local Voice AI Agent

100% local voice AI agent combining Sofia's personality with local voice processing.

## 🎯 Features

- **100% Local**: No cloud services, everything runs on your machine
- **Two Modes**: Console (terminal) and Browser (web UI)
- **Sofia's Personality**: All original tools and conversation management
- **Fast**: Real-time voice interaction

## 🔧 Technology Stack

| Component | Technology |
|-----------|------------|
| Speech-to-Text | Moonshine (HuggingFace) |
| Text-to-Speech | Kokoro ONNX |
| Language Model | Ollama (gemma3:4b) |
| Browser Mode | FastRTC + Gradio |
| Console Mode | PyAudio |

## 📋 Prerequisites

1. **Ollama must be running**:
   ```bash
   ollama serve
   ```

2. **Model must be pulled**:
   ```bash
   ollama pull gemma3:4b
   ```

3. **Python 3.10+** installed

## 🚀 Quick Start

### 1. Installation

```bash
# Already done for you!
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Sofia

#### Option A: Browser Mode (Recommended)
```bash
./run_dev.sh
# OR
.venv/bin/python agent.py dev
```

Browser will open automatically with voice interface.

#### Option B: Console Mode (Terminal)
```bash
./run_console.sh
# OR
.venv/bin/python agent.py console
```

Speak directly in terminal (press Ctrl+C to stop speaking).

## 📖 Usage

### Browser Mode (`python agent.py dev`)

1. Run the command
2. Browser opens with Gradio UI
3. Click microphone button
4. Start speaking
5. Sofia responds with voice
6. Say "goodbye" to end conversation

### Console Mode (`python agent.py console`)

1. Run the command
2. Wait for "🎤 Listening..."
3. Speak your message
4. Press Ctrl+C when done speaking
5. Sofia responds
6. Repeat or say "goodbye" to end

## 🛠️ Troubleshooting

### Ollama Not Running
```
❌ Error: Cannot connect to Ollama

Solution:
ollama serve
```

### Model Not Found
```
❌ Error: Model gemma3:4b not found

Solution:
ollama pull gemma3:4b
```

### Audio Device Issues (macOS)
- Console mode: Grant microphone permissions in System Settings
- Browser mode: Allow microphone access in browser

### Import Errors
```
❌ ModuleNotFoundError

Solution:
source .venv/bin/activate
pip install -r requirements.txt
```

## 📁 Project Structure

```
sofia-integrated/
├── agent.py                    # Main entry point
├── run_console.sh              # Helper script for console mode
├── run_dev.sh                  # Helper script for browser mode
├── requirements.txt            # Dependencies
├── src/
│   ├── agent/
│   │   ├── prompts.py         # Sofia's personality
│   │   ├── tools_local.py     # Sofia's tools
│   │   └── sofia_local.py     # Main agent class
│   └── voice/
│       ├── stt.py             # Speech-to-Text (Moonshine)
│       ├── tts.py             # Text-to-Speech (Kokoro)
│       ├── llm.py             # LLM integration (Ollama)
│       ├── console_handler.py # Console mode handler
│       └── browser_handler.py # Browser mode handler
└── .venv/                      # Virtual environment
```

## ✨ Comparison with LiveKit Version

| Feature | LiveKit (Original) | Sofia Integrated (Local) |
|---------|-------------------|--------------------------|
| Cloud dependency | ✅ Required | ❌ None |
| Voice processing | Google Gemini | Moonshine + Kokoro |
| LLM | Google Gemini | Ollama gemma3:4b |
| Tools | ✅ All included | ✅ All included |
| Personality | ✅ Sofia | ✅ Same Sofia |
| Browser UI | ✅ Yes | ✅ Yes (Gradio) |
| Console mode | ❌ Not really | ✅ True console |
| Cost | 💰 Pay per use | 🆓 Free |
| Privacy | ⚠️ Cloud | 🔒 100% local |

## 🎯 Next Steps

### Test Browser Mode
```bash
./run_dev.sh
```

### Test Console Mode
```bash
./run_console.sh
```

### Customize Sofia
Edit `src/agent/prompts.py` to change personality.
Edit `src/agent/tools_local.py` to add new functions.

## 💡 Tips

- **Browser mode is more reliable** than console mode on macOS
- **Keep Ollama running** in the background
- **Say "goodbye"** to end conversations gracefully
- **Speak clearly** for better transcription accuracy

## ⚙️ Configuration

### Change Ollama Model
Edit `src/agent/sofia_local.py`:
```python
def __init__(self, model: str = "gemma3:4b"):  # Change model here
```

### Adjust Voice Settings
Edit `src/voice/tts.py` for TTS settings
Edit `src/voice/stt.py` for STT settings

## 🐛 Known Issues

1. **Console mode audio device conflicts on macOS**: Browser mode recommended
2. **First run is slow**: Models need to download (1-2GB)
3. **Response time**: 2-3 seconds due to local processing (normal)

## 📝 License

Same as sofia-en (original repository)

---

**Built with ❤️ combining sofia-en + local-voice-ai-agent**