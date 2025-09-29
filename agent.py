#!/usr/bin/env python3
"""
Sofia Integrated Agent - Local Voice AI

Entry point for Sofia with local voice processing:
- python agent.py console → Terminal-based voice interaction
- python agent.py dev → Browser-based voice interaction (Gradio UI)

Uses:
- Moonshine STT (Speech-to-Text)
- Kokoro TTS (Text-to-Speech)
- Ollama gemma3:4b (Language Model)
- Sofia's personality and tools
"""
import sys
import os


def print_banner():
    """Print Sofia banner"""
    print("\n" + "=" * 60)
    print("   _____ ____  ______ _____   ___                    ")
    print("  / ___// __ \\/ ____//  _/  /   |                    ")
    print("  \\__ \\/ / / / /_    / /   / /| |                    ")
    print(" ___/ / /_/ / __/  _/ /   / ___ |                    ")
    print("/____/\\____/_/    /___/  /_/  |_|                    ")
    print("")
    print("         Local Voice AI Assistant")
    print("=" * 60)
    print("🎤 STT: Moonshine")
    print("🔊 TTS: Kokoro")
    print("🤖 LLM: Ollama (gemma3:4b)")
    print("=" * 60)


def print_usage():
    """Print usage information"""
    print("\n📖 USAGE:")
    print("  python agent.py console  → Terminal-based voice interaction")
    print("  python agent.py dev      → Browser-based voice interaction")
    print("\n💡 EXAMPLES:")
    print("  python agent.py console  # Run Sofia in terminal")
    print("  python agent.py dev      # Run Sofia in browser\n")


def check_dependencies():
    """Check if required dependencies are available"""
    missing = []

    try:
        import pyaudio
    except ImportError:
        missing.append("pyaudio")

    try:
        import fastrtc
    except ImportError:
        missing.append("fastrtc")

    try:
        import ollama
        # Check if Ollama is running
        try:
            ollama.list()
        except Exception:
            print("⚠️  WARNING: Ollama is not running!")
            print("   Start Ollama: ollama serve")
            print("   Pull model: ollama pull gemma3:4b\n")
    except ImportError:
        missing.append("ollama")

    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("   Install: pip install -r requirements.txt")
        return False

    return True


def main():
    """Main entry point"""
    print_banner()

    # Check arguments
    if len(sys.argv) < 2:
        print("❌ ERROR: Mode not specified")
        print_usage()
        sys.exit(1)

    mode = sys.argv[1].lower()

    # Validate mode
    if mode not in ["console", "dev"]:
        print(f"❌ ERROR: Invalid mode '{mode}'")
        print_usage()
        sys.exit(1)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Run appropriate mode
    try:
        if mode == "console":
            print("\n🎙️  Starting CONSOLE mode...")
            print("=" * 60)
            from src.voice.console_handler import run_console_mode
            run_console_mode()

        elif mode == "dev":
            print("\n🌐 Starting BROWSER mode...")
            print("=" * 60)
            from src.voice.browser_handler import run_browser_mode
            run_browser_mode()

    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("   Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()