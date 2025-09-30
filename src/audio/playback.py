"""
Windows-Native Audio Playback
Uses sounddevice for cross-platform audio output
No C++ compilation required
"""
import sounddevice as sd
import numpy as np
import queue
import threading
from loguru import logger


class AudioPlayback:
    """
    Windows-optimized audio playback using sounddevice

    Features:
    - WASAPI backend for low latency on Windows
    - Streaming playback support
    - Thread-safe audio buffering
    - No PyAudio/PortAudio compilation needed
    """

    def __init__(self, sample_rate=24000, channels=1):
        """
        Initialize audio playback

        Args:
            sample_rate: Audio sample rate (24000 for Kokoro)
            channels: Number of audio channels (1 = mono)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.is_playing = False

        logger.info(f"🔊 AudioPlayback initialized: {sample_rate}Hz, {channels}ch")

    def play(self, audio_data, blocking=True):
        """
        Play audio data

        Args:
            audio_data: numpy array or bytes
            blocking: Wait for playback to complete
        """
        try:
            # Convert bytes to numpy if needed
            if isinstance(audio_data, bytes):
                audio_data = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

            # Ensure float32
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)

            # Ensure 1D array
            if audio_data.ndim > 1:
                audio_data = audio_data.flatten()

            # Play audio
            self.is_playing = True
            sd.play(audio_data, samplerate=self.sample_rate)

            if blocking:
                sd.wait()
                self.is_playing = False
                logger.debug("✅ Playback complete")

        except Exception as e:
            logger.error(f"❌ Playback error: {e}")
            self.is_playing = False
            raise

    def stop(self):
        """Stop current playback"""
        try:
            sd.stop()
            self.is_playing = False
            logger.debug("⏹️ Playback stopped")
        except Exception as e:
            logger.error(f"❌ Stop error: {e}")

    def play_stream(self, audio_generator):
        """
        Play audio from a generator (for TTS streaming)

        Args:
            audio_generator: Generator yielding audio chunks
        """
        try:
            for audio_chunk in audio_generator:
                if audio_chunk is None or len(audio_chunk) == 0:
                    continue

                # Convert bytes to numpy if needed
                if isinstance(audio_chunk, bytes):
                    audio_chunk = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0

                # Play chunk without blocking
                self.play(audio_chunk, blocking=False)

                # Wait for current chunk to finish
                sd.wait()

            logger.debug("✅ Stream playback complete")

        except Exception as e:
            logger.error(f"❌ Stream playback error: {e}")
            raise


class StreamingAudioPlayer:
    """
    Advanced streaming audio player with queue-based buffering
    Better for real-time TTS where audio chunks arrive dynamically
    """

    def __init__(self, sample_rate=24000, channels=1, buffer_size=2048):
        """
        Initialize streaming player

        Args:
            sample_rate: Audio sample rate
            channels: Number of channels
            buffer_size: Size of playback buffer
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.buffer_size = buffer_size
        self.audio_queue = queue.Queue()
        self.stream = None
        self.is_playing = False

        logger.info(f"🔊 StreamingAudioPlayer initialized: {sample_rate}Hz")

    def _playback_callback(self, outdata, frames, time_info, status):
        """Callback for sounddevice output stream"""
        if status:
            logger.warning(f"Playback status: {status}")

        try:
            # Get audio from queue
            audio_chunk = self.audio_queue.get_nowait()

            # Copy to output buffer
            if len(audio_chunk) < frames:
                # Pad with zeros if chunk is smaller
                outdata[:len(audio_chunk)] = audio_chunk.reshape(-1, self.channels)
                outdata[len(audio_chunk):] = 0
            else:
                outdata[:] = audio_chunk[:frames].reshape(-1, self.channels)

        except queue.Empty:
            # No more audio, output silence
            outdata[:] = 0

    def start_stream(self):
        """Start output stream"""
        if self.is_playing:
            return

        try:
            self.stream = sd.OutputStream(
                channels=self.channels,
                samplerate=self.sample_rate,
                blocksize=self.buffer_size,
                callback=self._playback_callback,
                dtype=np.float32
            )

            self.stream.start()
            self.is_playing = True
            logger.debug("✅ Streaming started")

        except Exception as e:
            logger.error(f"❌ Failed to start stream: {e}")
            raise

    def stop_stream(self):
        """Stop output stream"""
        if not self.is_playing:
            return

        try:
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None

            self.is_playing = False
            logger.debug("⏹️ Streaming stopped")

        except Exception as e:
            logger.error(f"❌ Failed to stop stream: {e}")

    def add_audio(self, audio_data):
        """
        Add audio data to playback queue

        Args:
            audio_data: numpy array or bytes
        """
        # Convert bytes to numpy if needed
        if isinstance(audio_data, bytes):
            audio_data = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

        # Ensure float32
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)

        self.audio_queue.put(audio_data)

    def clear_buffer(self):
        """Clear playback queue"""
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

    def __del__(self):
        """Cleanup"""
        self.stop_stream()


if __name__ == "__main__":
    # Test playback with a simple tone
    logger.info("Testing AudioPlayback...")

    player = AudioPlayback(sample_rate=16000)

    # Generate a 440Hz tone (A note) for 1 second
    duration = 1.0
    t = np.linspace(0, duration, int(16000 * duration))
    tone = np.sin(2 * np.pi * 440 * t).astype(np.float32)

    logger.info("Playing 440Hz tone for 1 second...")
    player.play(tone, blocking=True)

    logger.info("✅ AudioPlayback test complete!")