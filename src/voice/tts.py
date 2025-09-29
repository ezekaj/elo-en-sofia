"""
Text-to-Speech Module using Kokoro
Wrapper around fastrtc's TTS model
"""
from fastrtc import get_tts_model
import numpy as np


class TextToSpeech:
    def __init__(self):
        """Initialize Kokoro TTS model"""
        print("🔊 Loading Kokoro TTS model...")
        self.model = get_tts_model()  # Kokoro v1.0 ONNX
        print("✅ Kokoro TTS loaded successfully")

    def synthesize(self, text, speed=1.0):
        """
        Synthesize text to speech (streaming)

        Args:
            text (str): Text to convert to speech
            speed (float): Speech speed multiplier (default: 1.0)

        Yields:
            Audio chunks as bytes (converted from numpy arrays)
        """
        try:
            # Clean up text for better pronunciation
            text = text.replace("'", "'").replace('"', '"')

            for sample_rate, audio_array in self.model.stream_tts_sync(text):
                # Convert numpy array to bytes for PyAudio
                # audio_array is float32, need to convert to int16
                # Reduce volume slightly for softer sound (0.8 instead of 1.0)
                audio_int16 = (audio_array * 32767 * 0.8).astype(np.int16)
                audio_bytes = audio_int16.tobytes()
                yield audio_bytes
        except Exception as e:
            print(f"❌ TTS Error: {e}")
            import traceback
            traceback.print_exc()
            return

    def synthesize_blocking(self, text):
        """
        Synthesize text to speech (blocking, returns all audio)

        Args:
            text (str): Text to convert to speech

        Returns:
            bytes: Complete audio data
        """
        audio_chunks = []
        for chunk in self.synthesize(text):
            audio_chunks.append(chunk)
        return b''.join(audio_chunks) if audio_chunks else b''