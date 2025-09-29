"""
Speech-to-Text Module using Moonshine
Wrapper around fastrtc's STT model
"""
from fastrtc import get_stt_model
import numpy as np


class SpeechToText:
    def __init__(self):
        """Initialize Moonshine STT model"""
        print("🎤 Loading Moonshine STT model...")
        self.model = get_stt_model()  # Moonshine base
        print("✅ Moonshine STT loaded successfully")

    def transcribe(self, audio_data, sample_rate=16000):
        """
        Transcribe audio to text

        Args:
            audio_data: Audio data as bytes (from PyAudio)
            sample_rate: Sample rate of audio (default: 16000)

        Returns:
            str: Transcribed text
        """
        try:
            # Convert bytes to numpy array
            audio_np = np.frombuffer(audio_data, dtype=np.int16)

            # Convert to float32 and normalize
            audio_float = audio_np.astype(np.float32) / 32768.0

            # STT expects (sample_rate, audio_array) tuple
            transcript = self.model.stt((sample_rate, audio_float))
            return transcript.strip()
        except Exception as e:
            print(f"❌ STT Error: {e}")
            import traceback
            traceback.print_exc()
            return ""

    def transcribe_streaming(self, audio_chunks):
        """
        Transcribe audio stream (for future use)

        Args:
            audio_chunks: Iterator of audio chunks

        Yields:
            str: Partial transcriptions
        """
        # Future implementation for streaming STT
        for chunk in audio_chunks:
            yield self.transcribe(chunk)