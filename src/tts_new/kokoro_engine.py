"""
Windows-Native Text-to-Speech using Kokoro ONNX
Direct integration without fastrtc dependency
High-quality neural TTS optimized for Windows
"""
from kokoro_onnx import Kokoro
import numpy as np
from loguru import logger
import os
from pathlib import Path
import urllib.request


class KokoroTTS:
    """
    Text-to-Speech using Kokoro ONNX

    Features:
    - High-quality neural voice synthesis
    - ONNX runtime (optimized for Windows)
    - Multiple voices available
    - Fast inference (~100-200ms)
    - No fastrtc/WebRTC complexity

    Voices:
    - af: Female voice (default)
    - am: Male voice
    - bf: Female voice (British)
    - bm: Male voice (British)
    """

    # Model URLs
    MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
    VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"

    # Available voices (common ones for easy access)
    VOICES = ['af_bella', 'af_nicole', 'af_sarah', 'af_nova',
              'am_adam', 'am_michael', 'bf_emma', 'bm_george']

    def __init__(self, voice='af_bella', speed=1.0):
        """
        Initialize Kokoro TTS

        Args:
            voice: Voice ID (default: 'af' - American Female)
            speed: Speech speed multiplier (0.5-2.0, default: 1.0)
        """
        self.voice = voice
        self.speed = speed
        self.model = None
        self.model_dir = Path.home() / '.kokoro_models'

        logger.info(f"🔊 Initializing Kokoro TTS: voice={voice}, speed={speed}x")

        # Model will be lazy-loaded on first use
        self._load_model()

    def _download_model(self, url, destination):
        """Download model file if not exists"""
        if destination.exists():
            logger.info(f"✅ Model file already exists: {destination.name}")
            return

        logger.info(f"📥 Downloading {destination.name} (~300MB, may take 2-5 minutes)...")
        destination.parent.mkdir(parents=True, exist_ok=True)

        try:
            def show_progress(block_num, block_size, total_size):
                downloaded = block_num * block_size
                percent = min(100, downloaded * 100 / total_size) if total_size > 0 else 0
                if block_num % 50 == 0:  # Update every 50 blocks
                    logger.info(f"  Progress: {percent:.1f}% ({downloaded / (1024*1024):.1f} MB)")

            urllib.request.urlretrieve(url, str(destination), show_progress)
            logger.info(f"✅ Downloaded {destination.name}")
        except Exception as e:
            logger.error(f"❌ Failed to download {destination.name}: {e}")
            # Clean up partial download
            if destination.exists():
                destination.unlink()
            raise

    def _load_model(self):
        """Load Kokoro model (lazy loading)"""
        if self.model is not None:
            return

        try:
            logger.info("📥 Loading Kokoro TTS model...")

            # Ensure model directory exists
            self.model_dir.mkdir(parents=True, exist_ok=True)

            # Model paths
            model_path = self.model_dir / 'kokoro-v1.0.onnx'
            voices_path = self.model_dir / 'voices-v1.0.bin'

            # Download models if needed
            self._download_model(self.MODEL_URL, model_path)
            self._download_model(self.VOICES_URL, voices_path)

            # Initialize Kokoro with model files
            self.model = Kokoro(str(model_path), str(voices_path))

            logger.info("✅ Kokoro TTS loaded successfully")

        except Exception as e:
            logger.error(f"❌ Failed to load Kokoro TTS: {e}")
            raise

    def synthesize(self, text, speed=None):
        """
        Synthesize text to speech

        Args:
            text: Text to synthesize
            speed: Override default speed (optional)

        Returns:
            tuple: (sample_rate, audio_array)
                sample_rate: Audio sample rate (typically 24000)
                audio_array: numpy array (float32, range -1 to 1)
        """
        try:
            # Ensure model is loaded
            self._load_model()

            # Use provided speed or default
            synthesis_speed = speed if speed is not None else self.speed

            # Clean text for better pronunciation
            text = self._clean_text(text)

            if not text.strip():
                logger.warning("Empty text provided to TTS")
                return 24000, np.array([], dtype=np.float32)

            # Generate speech with voice parameter
            audio, sample_rate = self.model.create(
                text,
                voice=self.voice,
                speed=synthesis_speed,
                lang='en-us'
            )

            # Ensure float32
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)

            # Normalize audio to prevent clipping
            max_val = np.abs(audio).max()
            if max_val > 0:
                audio = audio / max_val * 0.8  # Scale to 80% to avoid clipping

            return sample_rate, audio

        except Exception as e:
            logger.error(f"❌ TTS Error: {e}")
            import traceback
            traceback.print_exc()
            return 24000, np.array([], dtype=np.float32)

    def synthesize_streaming(self, text, speed=None):
        """
        Synthesize text with streaming output (chunk by chunk)

        Args:
            text: Text to synthesize
            speed: Override default speed (optional)

        Yields:
            tuple: (sample_rate, audio_chunk)
        """
        try:
            self._load_model()

            synthesis_speed = speed if speed is not None else self.speed
            text = self._clean_text(text)

            if not text.strip():
                return

            # Split text into sentences for streaming
            sentences = self._split_into_sentences(text)

            for sentence in sentences:
                if not sentence.strip():
                    continue

                audio, sample_rate = self.model.create(
                    sentence,
                    voice=self.voice,
                    speed=synthesis_speed,
                    lang='en-us'
                )

                # Ensure float32
                if audio.dtype != np.float32:
                    audio = audio.astype(np.float32)

                # Normalize
                max_val = np.abs(audio).max()
                if max_val > 0:
                    audio = audio / max_val * 0.8

                yield sample_rate, audio

        except Exception as e:
            logger.error(f"❌ TTS Streaming Error: {e}")

    def _clean_text(self, text):
        """
        Clean text for better TTS pronunciation

        Args:
            text: Input text

        Returns:
            str: Cleaned text
        """
        # Replace special quotes with regular quotes
        text = text.replace("'", "'").replace("'", "'")
        text = text.replace(""", '"').replace(""", '"')

        # Remove multiple spaces
        text = ' '.join(text.split())

        # Ensure sentence ends with punctuation
        if text and not text[-1] in '.!?':
            text += '.'

        return text

    def _split_into_sentences(self, text):
        """
        Split text into sentences for streaming

        Args:
            text: Input text

        Returns:
            list: List of sentences
        """
        import re

        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)

        return [s.strip() for s in sentences if s.strip()]

    def change_voice(self, voice):
        """
        Change to a different voice

        Args:
            voice: Voice ID
        """
        if voice not in self.VOICES:
            logger.warning(f"Unknown voice '{voice}', available: {self.VOICES}")
            return

        logger.info(f"🔄 Changing voice to {voice}...")
        self.voice = voice

    def set_speed(self, speed):
        """
        Set speech speed

        Args:
            speed: Speed multiplier (0.5-2.0)
        """
        if speed < 0.5 or speed > 2.0:
            logger.warning(f"Speed {speed} out of range [0.5-2.0], clamping")
            speed = max(0.5, min(2.0, speed))

        self.speed = speed
        logger.info(f"🎚️ Speed set to {speed}x")


# Convenience function for quick TTS
def synthesize_text(text, voice='af_bella', speed=1.0):
    """
    Quick function to synthesize text

    Args:
        text: Text to synthesize
        voice: Voice ID
        speed: Speech speed

    Returns:
        tuple: (sample_rate, audio_array)
    """
    tts = KokoroTTS(voice=voice, speed=speed)
    return tts.synthesize(text)


if __name__ == "__main__":
    # Test Kokoro TTS
    logger.info("Testing KokoroTTS...")

    tts = KokoroTTS(voice='af_bella')

    test_text = "Hello! This is a test of the Kokoro text to speech system. It works great on Windows!"

    logger.info(f"Synthesizing: '{test_text}'")
    sample_rate, audio = tts.synthesize(test_text)

    logger.info(f"Generated {len(audio)} samples at {sample_rate}Hz ({len(audio)/sample_rate:.2f} seconds)")

    # Test streaming
    logger.info("\nTesting streaming synthesis...")
    for i, (sr, chunk) in enumerate(tts.synthesize_streaming(test_text)):
        logger.info(f"  Chunk {i+1}: {len(chunk)} samples")

    logger.info("✅ KokoroTTS test complete!")
    logger.info("💡 Audio generated but not played (use AudioPlayback to play)")