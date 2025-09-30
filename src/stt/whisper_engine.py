"""
Windows-Native Speech-to-Text using faster-whisper
Optimized OpenAI Whisper with CTranslate2 backend
No WebRTC complexity - pure Python with Windows optimization
"""
from faster_whisper import WhisperModel
import numpy as np
from loguru import logger
from pathlib import Path


class WhisperSTT:
    """
    Speech-to-Text using faster-whisper

    Features:
    - Optimized for Windows with Intel MKL/OpenBLAS
    - Multiple model sizes (tiny, base, small, medium, large)
    - Fast inference (~200-500ms for short audio)
    - High accuracy
    - No WebRTC/fastrtc dependencies

    Performance on Windows:
    - tiny.en: ~75MB, ~200ms, good for real-time
    - base.en: ~150MB, ~300ms, better accuracy
    - small.en: ~500MB, ~500ms, high accuracy
    """

    MODEL_SIZES = {
        'tiny': 'tiny',
        'tiny.en': 'tiny.en',
        'base': 'base',
        'base.en': 'base.en',
        'small': 'small',
        'small.en': 'small.en',
    }

    def __init__(self, model_size='tiny.en', device='cpu', compute_type='int8'):
        """
        Initialize Whisper STT

        Args:
            model_size: Model size ('tiny.en', 'base.en', 'small.en')
            device: 'cpu' or 'cuda'
            compute_type: 'int8', 'int8_float16', 'float16', 'float32'
                         'int8' is fastest for CPU, good quality
        """
        if model_size not in self.MODEL_SIZES:
            logger.warning(f"Unknown model size {model_size}, using 'tiny.en'")
            model_size = 'tiny.en'

        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None

        logger.info(f"🎤 Initializing Whisper STT: {model_size} on {device}")
        logger.info(f"   Compute type: {compute_type}")

        # Model will be lazy-loaded on first use
        self._load_model()

    def _load_model(self):
        """Load Whisper model (lazy loading)"""
        if self.model is not None:
            return

        try:
            logger.info("📥 Loading Whisper model (this may take a moment on first run)...")

            # Download and load model
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
                download_root=None  # Uses default cache location
            )

            logger.info("✅ Whisper model loaded successfully")

        except Exception as e:
            logger.error(f"❌ Failed to load Whisper model: {e}")
            raise

    def transcribe(self, audio_data, sample_rate=16000, language='en'):
        """
        Transcribe audio to text

        Args:
            audio_data: numpy array (float32) or bytes (int16)
            sample_rate: Audio sample rate (16000 for Whisper)
            language: Language code ('en' for English)

        Returns:
            str: Transcribed text
        """
        try:
            # Ensure model is loaded
            self._load_model()

            # Convert bytes to numpy if needed
            if isinstance(audio_data, bytes):
                audio_data = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

            # Ensure float32
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)

            # Ensure 1D
            if audio_data.ndim > 1:
                audio_data = audio_data.flatten()

            # faster-whisper expects float32 array at 16kHz
            # Resample if needed (though we should always capture at 16kHz)
            if sample_rate != 16000:
                logger.warning(f"Audio is {sample_rate}Hz, Whisper expects 16000Hz")
                # Simple resampling (use scipy for better quality if needed)
                audio_data = self._resample(audio_data, sample_rate, 16000)

            # Transcribe
            # beam_size=1 for speed, higher for accuracy
            # vad_filter=True uses Whisper's built-in VAD
            segments, info = self.model.transcribe(
                audio_data,
                language=language,
                beam_size=1,  # Faster, use 5 for better quality
                vad_filter=True,
                vad_parameters=dict(min_silence_duration_ms=500)
            )

            # Concatenate all segments
            text = ' '.join([segment.text for segment in segments])

            return text.strip()

        except Exception as e:
            logger.error(f"❌ STT Error: {e}")
            import traceback
            traceback.print_exc()
            return ""

    def transcribe_with_timestamps(self, audio_data, sample_rate=16000, language='en'):
        """
        Transcribe with word-level timestamps

        Args:
            audio_data: numpy array or bytes
            sample_rate: Audio sample rate
            language: Language code

        Returns:
            list: List of dicts with {text, start, end}
        """
        try:
            self._load_model()

            # Prepare audio
            if isinstance(audio_data, bytes):
                audio_data = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)

            if audio_data.ndim > 1:
                audio_data = audio_data.flatten()

            if sample_rate != 16000:
                audio_data = self._resample(audio_data, sample_rate, 16000)

            # Transcribe with word timestamps
            segments, info = self.model.transcribe(
                audio_data,
                language=language,
                beam_size=1,
                word_timestamps=True,
                vad_filter=True
            )

            # Extract segments with timestamps
            results = []
            for segment in segments:
                results.append({
                    'text': segment.text.strip(),
                    'start': segment.start,
                    'end': segment.end
                })

            return results

        except Exception as e:
            logger.error(f"❌ STT with timestamps error: {e}")
            return []

    def _resample(self, audio, orig_sr, target_sr):
        """
        Simple audio resampling
        For production, use scipy.signal.resample or librosa
        """
        if orig_sr == target_sr:
            return audio

        # Simple linear interpolation
        duration = len(audio) / orig_sr
        target_length = int(duration * target_sr)

        from scipy import signal
        return signal.resample(audio, target_length)

    def change_model(self, model_size):
        """
        Change to a different Whisper model

        Args:
            model_size: New model size
        """
        if model_size not in self.MODEL_SIZES:
            logger.error(f"Invalid model size: {model_size}")
            return

        logger.info(f"🔄 Changing model to {model_size}...")
        self.model_size = model_size
        self.model = None  # Force reload
        self._load_model()


# Convenience function for quick transcription
def transcribe_audio(audio_data, sample_rate=16000, model_size='tiny.en'):
    """
    Quick function to transcribe audio

    Args:
        audio_data: numpy array or bytes
        sample_rate: Audio sample rate
        model_size: Whisper model size

    Returns:
        str: Transcribed text
    """
    stt = WhisperSTT(model_size=model_size)
    return stt.transcribe(audio_data, sample_rate)


if __name__ == "__main__":
    # Test Whisper STT
    logger.info("Testing WhisperSTT...")

    stt = WhisperSTT(model_size='tiny.en')

    # Create a silent audio sample (just for testing import)
    test_audio = np.zeros(16000, dtype=np.float32)  # 1 second of silence

    logger.info("Transcribing 1 second of silence (should return empty)...")
    result = stt.transcribe(test_audio)

    logger.info(f"Result: '{result}'")
    logger.info("✅ WhisperSTT test complete!")
    logger.info("💡 Speak into your microphone to test with real audio")