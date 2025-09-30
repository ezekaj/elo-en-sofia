"""
Master Test Runner
Runs all test suites and generates comprehensive report
"""
import sys
import os
from loguru import logger

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tests.test_audio import run_all_audio_tests
from tests.test_stt import run_all_stt_tests
from tests.test_tts import run_all_tts_tests
from tests.test_llm import run_all_llm_tests
from tests.test_pipeline import run_all_pipeline_tests


def main():
    """Run all test suites"""
    logger.info("\n" + "=" * 80)
    logger.info("  SOFIA WINDOWS-NATIVE - COMPLETE TEST SUITE")
    logger.info("=" * 80)

    interactive = '--interactive' in sys.argv

    if interactive:
        logger.info("\n🎤 INTERACTIVE MODE ENABLED")
        logger.info("Tests will include microphone and audio playback")
        logger.info("Make sure your microphone and speakers are working!")
    else:
        logger.info("\n🤖 AUTOMATIC MODE")
        logger.info("Use --interactive flag to enable microphone/playback tests")

    # Test results
    results = {}

    # Run test suites
    logger.info("\n" + "=" * 80)
    logger.info("  STARTING TEST SUITES")
    logger.info("=" * 80)

    try:
        logger.info("\n[1/5] Running Audio Tests...")
        results['Audio'] = run_all_audio_tests()
    except Exception as e:
        logger.error(f"Audio tests crashed: {e}")
        results['Audio'] = False

    try:
        logger.info("\n[2/5] Running STT Tests...")
        results['STT'] = run_all_stt_tests(interactive=interactive)
    except Exception as e:
        logger.error(f"STT tests crashed: {e}")
        results['STT'] = False

    try:
        logger.info("\n[3/5] Running TTS Tests...")
        results['TTS'] = run_all_tts_tests(interactive=interactive)
    except Exception as e:
        logger.error(f"TTS tests crashed: {e}")
        results['TTS'] = False

    try:
        logger.info("\n[4/5] Running LLM Tests...")
        results['LLM'] = run_all_llm_tests()
    except Exception as e:
        logger.error(f"LLM tests crashed: {e}")
        results['LLM'] = False

    try:
        logger.info("\n[5/5] Running Pipeline Tests...")
        results['Pipeline'] = run_all_pipeline_tests(interactive=interactive)
    except Exception as e:
        logger.error(f"Pipeline tests crashed: {e}")
        results['Pipeline'] = False

    # Final summary
    logger.info("\n" + "=" * 80)
    logger.info("  FINAL TEST REPORT")
    logger.info("=" * 80)

    passed_suites = sum(1 for result in results.values() if result)
    total_suites = len(results)

    for suite_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{suite_name:20s}: {status}")

    logger.info("\n" + "-" * 80)
    logger.info(f"Total: {passed_suites}/{total_suites} test suites passed ({passed_suites/total_suites*100:.1f}%)")
    logger.info("=" * 80)

    if passed_suites == total_suites:
        logger.info("\n🎉 ALL TESTS PASSED!")
        logger.info("✅ Sofia Windows-Native is ready to use!")
        logger.info("\nRun Sofia with:")
        logger.info("  python agent-windows.py gradio    # Web interface")
        logger.info("  python agent-windows.py console   # Terminal interface")
        return 0
    else:
        logger.warning("\n⚠️ SOME TESTS FAILED")
        logger.warning("Please review the failures above and fix issues before using Sofia")

        # Provide guidance
        failed_suites = [name for name, result in results.items() if not result]

        if 'Audio' in failed_suites:
            logger.error("\n❌ Audio system issues:")
            logger.error("  - Check microphone/speaker connections")
            logger.error("  - Verify Windows audio device settings")
            logger.error("  - Run: test-audio.bat")

        if 'STT' in failed_suites:
            logger.error("\n❌ Speech-to-Text issues:")
            logger.error("  - Whisper model may not be downloaded")
            logger.error("  - Check internet connection for first run")
            logger.error("  - Try: python tests/test_stt.py")

        if 'TTS' in failed_suites:
            logger.error("\n❌ Text-to-Speech issues:")
            logger.error("  - Kokoro model may not be installed")
            logger.error("  - Try: pip install --upgrade kokoro-onnx")

        if 'LLM' in failed_suites:
            logger.error("\n❌ LLM issues:")
            logger.error("  - Make sure Ollama is running: ollama serve")
            logger.error("  - Pull model: ollama pull gemma3:4b")
            logger.error("  - Check: ollama list")

        if 'Pipeline' in failed_suites:
            logger.error("\n❌ Pipeline integration issues:")
            logger.error("  - Fix individual component issues first")
            logger.error("  - Then retry pipeline tests")

        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)