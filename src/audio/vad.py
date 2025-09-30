"""
Voice Activity Detection (VAD)
Uses webrtcvad-wheels (pre-built, no compilation)
"""
import webrtcvad
import numpy as np
from collections import deque
from loguru import logger


class VoiceActivityDetector:
    """
    Detect speech in audio using WebRTC VAD

    Features:
    - Optimized for speech detection
    - Configurable aggressiveness
    - Frame-based processing
    - Works with sounddevice audio
    """

    def __init__(self, sample_rate=16000, aggressiveness=2):
        """
        Initialize VAD

        Args:
            sample_rate: Must be 8000, 16000, 32000, or 48000
            aggressiveness: 0-3, higher = more aggressive filtering
        """
        if sample_rate not in [8000, 16000, 32000, 48000]:
            raise ValueError("Sample rate must be 8000, 16000, 32000, or 48000")

        self.sample_rate = sample_rate
        self.vad = webrtcvad.Vad(aggressiveness)

        # Frame duration in ms (must be 10, 20, or 30)
        self.frame_duration_ms = 30
        self.frame_size = int(sample_rate * self.frame_duration_ms / 1000)

        logger.info(f"🎙️ VAD initialized: {sample_rate}Hz, aggressiveness={aggressiveness}")

    def is_speech(self, audio_frame):
        """
        Check if audio frame contains speech

        Args:
            audio_frame: numpy array (float32) or bytes (int16)

        Returns:
            bool: True if speech detected
        """
        try:
            # Convert float32 to int16 bytes if needed
            if isinstance(audio_frame, np.ndarray):
                if audio_frame.dtype == np.float32:
                    audio_frame = (audio_frame * 32768).astype(np.int16)
                audio_bytes = audio_frame.tobytes()
            else:
                audio_bytes = audio_frame

            # VAD requires exact frame size
            expected_bytes = self.frame_size * 2  # 2 bytes per int16
            if len(audio_bytes) != expected_bytes:
                # Pad or truncate to correct size
                if len(audio_bytes) < expected_bytes:
                    audio_bytes += b'\x00' * (expected_bytes - len(audio_bytes))
                else:
                    audio_bytes = audio_bytes[:expected_bytes]

            return self.vad.is_speech(audio_bytes, self.sample_rate)

        except Exception as e:
            logger.warning(f"VAD error: {e}")
            return False

    def process_audio_buffer(self, audio_data, threshold=0.5):
        """
        Process entire audio buffer and determine if it contains speech

        Args:
            audio_data: numpy array of audio
            threshold: Fraction of frames that must contain speech (0-1)

        Returns:
            bool: True if speech detected above threshold
        """
        # Split into frames
        num_frames = len(audio_data) // self.frame_size
        speech_frames = 0

        for i in range(num_frames):
            start = i * self.frame_size
            end = start + self.frame_size
            frame = audio_data[start:end]

            if self.is_speech(frame):
                speech_frames += 1

        if num_frames == 0:
            return False

        speech_ratio = speech_frames / num_frames
        return speech_ratio >= threshold


class SpeechDetector:
    """
    Higher-level speech detection with start/end detection

    Useful for detecting when user starts and stops speaking
    """

    def __init__(self, sample_rate=16000, aggressiveness=2,
                 speech_padding_ms=300, silence_duration_ms=900):
        """
        Initialize speech detector

        Args:
            sample_rate: Audio sample rate
            aggressiveness: VAD aggressiveness (0-3)
            speech_padding_ms: Padding before/after speech
            silence_duration_ms: Silence duration to detect speech end
        """
        self.vad = VoiceActivityDetector(sample_rate, aggressiveness)
        self.sample_rate = sample_rate

        # Calculate frame counts
        frame_duration_ms = self.vad.frame_duration_ms
        self.speech_padding_frames = int(speech_padding_ms / frame_duration_ms)
        self.silence_duration_frames = int(silence_duration_ms / frame_duration_ms)

        # State tracking
        self.is_speech_active = False
        self.silence_frames = 0
        self.speech_frames = deque(maxlen=self.speech_padding_frames)

        logger.info(f"🗣️ SpeechDetector initialized: {sample_rate}Hz")

    def process_frame(self, audio_frame):
        """
        Process audio frame and detect speech state changes

        Args:
            audio_frame: numpy array or bytes

        Returns:
            tuple: (is_speaking, state_changed)
                is_speaking: Current speech state
                state_changed: True if state changed this frame
        """
        is_speech = self.vad.is_speech(audio_frame)
        state_changed = False

        if is_speech:
            self.silence_frames = 0

            if not self.is_speech_active:
                # Speech started
                self.is_speech_active = True
                state_changed = True
                logger.debug("🗣️ Speech started")
        else:
            if self.is_speech_active:
                self.silence_frames += 1

                if self.silence_frames >= self.silence_duration_frames:
                    # Speech ended
                    self.is_speech_active = False
                    state_changed = True
                    self.silence_frames = 0
                    logger.debug("🤐 Speech ended")

        return self.is_speech_active, state_changed

    def reset(self):
        """Reset detector state"""
        self.is_speech_active = False
        self.silence_frames = 0
        self.speech_frames.clear()


# Convenience function for simple VAD
def detect_speech(audio_data, sample_rate=16000, aggressiveness=2):
    """
    Simple function to detect if audio contains speech

    Args:
        audio_data: numpy array of audio
        sample_rate: Audio sample rate
        aggressiveness: VAD aggressiveness (0-3)

    Returns:
        bool: True if speech detected
    """
    vad = VoiceActivityDetector(sample_rate, aggressiveness)
    return vad.process_audio_buffer(audio_data, threshold=0.3)


if __name__ == "__main__":
    # Test VAD
    logger.info("Testing VoiceActivityDetector...")

    vad = VoiceActivityDetector(sample_rate=16000, aggressiveness=2)

    # Create silence (zeros)
    silence = np.zeros(vad.frame_size, dtype=np.float32)
    logger.info(f"Silence detected as speech: {vad.is_speech(silence)}")

    # Create noise (random)
    noise = np.random.randn(vad.frame_size).astype(np.float32) * 0.1
    logger.info(f"Noise detected as speech: {vad.is_speech(noise)}")

    # Create tone (simulated speech frequency)
    t = np.linspace(0, vad.frame_duration_ms/1000, vad.frame_size)
    tone = np.sin(2 * np.pi * 300 * t).astype(np.float32) * 0.5
    logger.info(f"Tone detected as speech: {vad.is_speech(tone)}")

    logger.info("✅ VAD test complete!")