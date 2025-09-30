#!/usr/bin/env python3
"""
Sofia Windows-Native Voice AI Assistant
Main entry point for the Windows-optimized version

Usage:
    python agent-windows.py gradio   # Web interface
    python agent-windows.py console  # Terminal interface
"""
import sys
import os
from loguru import logger

# Configure logger
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    level="INFO"
)


def print_banner():
    """Print Sofia banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ███████╗ ██████╗ ███████╗██╗ █████╗                       ║
║   ██╔════╝██╔═══██╗██╔════╝██║██╔══██╗                      ║
║   ███████╗██║   ██║█████╗  ██║███████║                      ║
║   ╚════██║██║   ██║██╔══╝  ██║██╔══██║                      ║
║   ███████║╚██████╔╝██║     ██║██║  ██║                      ║
║   ╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝                      ║
║                                                              ║
║         Windows-Native Voice AI Assistant                   ║
║         100% Local • No Cloud • Privacy-First               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

    🎤 STT: faster-whisper (tiny.en)
    🤖 LLM: Ollama (gemma3:4b)
    🔊 TTS: Kokoro ONNX
    🪟 Platform: Windows-Optimized
"""
    print(banner)


def print_usage():
    """Print usage information"""
    usage = """
Usage: python agent-windows.py <mode>

Modes:
  gradio     Launch web interface (recommended)
             Opens browser automatically at http://localhost:7860

  console    Launch terminal interface
             Voice-based interaction in console

Examples:
  python agent-windows.py gradio    # Web UI (easiest)
  python agent-windows.py console   # Terminal mode

For first-time users, we recommend the web interface (gradio mode).
"""
    print(usage)


def check_prerequisites():
    """Check if all prerequisites are met"""
    issues = []

    # Check Python version
    if sys.version_info < (3, 10):
        issues.append(f"❌ Python 3.10+ required (you have {sys.version_info.major}.{sys.version_info.minor})")

    # Check Ollama
    try:
        import ollama
        ollama.list()
        logger.info("✅ Ollama is running")
    except Exception as e:
        issues.append(f"❌ Ollama not running: {e}")
        issues.append("   Run: ollama serve")

    # Check dependencies
    missing_deps = []
    required = [
        'sounddevice', 'faster_whisper', 'kokoro_onnx',
        'gradio', 'loguru', 'ollama', 'numpy'
    ]

    for dep in required:
        try:
            __import__(dep)
        except ImportError:
            missing_deps.append(dep)

    if missing_deps:
        issues.append(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        issues.append("   Run: pip install -r requirements-windows.txt")

    return issues


def main():
    """Main entry point"""
    print_banner()

    # Check arguments
    if len(sys.argv) < 2:
        logger.error("❌ No mode specified")
        print_usage()
        sys.exit(1)

    mode = sys.argv[1].lower()

    # Validate mode
    if mode not in ['gradio', 'console']:
        logger.error(f"❌ Invalid mode: '{mode}'")
        print_usage()
        sys.exit(1)

    # Check prerequisites
    logger.info("🔍 Checking prerequisites...")
    issues = check_prerequisites()

    if issues:
        logger.error("❌ Prerequisites check failed:")
        for issue in issues:
            print(f"  {issue}")
        print("\nPlease fix the above issues and try again.")
        sys.exit(1)

    logger.info("✅ All prerequisites met")

    # Run appropriate mode
    try:
        if mode == 'gradio':
            logger.info("🌐 Starting Gradio web interface...")
            logger.info("=" * 60)
            logger.info("  Web UI will open in your browser automatically")
            logger.info("  If not, navigate to: http://localhost:7860")
            logger.info("=" * 60)

            from src.ui.gradio_app import GradioInterface

            app = GradioInterface()
            app.launch()

        elif mode == 'console':
            logger.info("🖥️ Starting console interface...")
            logger.info("=" * 60)

            from src.ui.console_app import ConsoleInterface

            app = ConsoleInterface()
            app.run()

    except KeyboardInterrupt:
        logger.info("\n\n👋 Goodbye!")
        sys.exit(0)

    except ImportError as e:
        logger.error(f"\n❌ Import Error: {e}")
        logger.error("\nMake sure all dependencies are installed:")
        logger.error("  pip install -r requirements-windows.txt")
        sys.exit(1)

    except Exception as e:
        logger.error(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()