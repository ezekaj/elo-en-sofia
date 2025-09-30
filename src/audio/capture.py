"""
Windows-Native Audio Capture
Uses sounddevice for cross-platform audio with Windows WASAPI support
No C++ compilation required - pure Python with pre-built wheels
"""
import sounddevice as sd
import numpy as np
import queue
import threading
from loguru import logger


class AudioCapture:
    """
    Windows-optimized audio capture using sounddevice

    Features:
    - WASAPI backend for low latency on Windows
    - Thread-safe audio buffering
    - Configurable sample rate and channels
    - No PyAudio/PortAudio compilation needed
    """

    def __init__(self, sample_rate=16000, channels=1, chunk_size=1024):
        """
        Initialize audio capture

        Args:
            sample_rate: Audio sample rate (16000 for Whisper)
            channels: Number of audio channels (1 = mono)
            chunk_size: Size of audio chunks to capture
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.audio_queue = queue.Queue()
        self.is_recording = False
        self.stream = None

        logger.info(f"🎤 AudioCapture initialized: {sample_rate}Hz, {channels}ch")

        # List available audio devices
        self._list_devices()

    def _list_devices(self):
        """List available audio input devices"""
        try:
            devices = sd.query_devices()
            logger.info("📻 Available audio devices:")
            for idx, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    logger.info(f"  [{idx}] {device['name']} (inputs: {device['max_input_channels']})")
        except Exception as e:
            logger.warning(f"Could not list audio devices: {e}")

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for sounddevice stream"""
        if status:
            logger.warning(f"Audio status: {status}")

        # Copy audio data to queue (indata is numpy array)
        audio_chunk = indata.copy()
        self.audio_queue.put(audio_chunk)

    def start_recording(self, device=None):
        """
        Start audio capture

        Args:
            device: Device index or None for default
        """
        if self.is_recording:
            logger.warning("Already recording!")
            return

        try:
            # Create input stream with WASAPI backend
            self.stream = sd.InputStream(
                device=device,
                channels=self.channels,
                samplerate=self.sample_rate,
                blocksize=self.chunk_size,
                callback=self._audio_callback,
                dtype=np.float32  # Use float32 for Whisper compatibility
            )

            self.stream.start()
            self.is_recording = True
            logger.info("✅ Recording started")

        except Exception as e:
            logger.error(f"❌ Failed to start recording: {e}")
            raise

    def stop_recording(self):
        """Stop audio capture"""
        if not self.is_recording:
            return

        try:
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None

            self.is_recording = False
            logger.info("⏹️ Recording stopped")

        except Exception as e:
            logger.error(f"❌ Failed to stop recording: {e}")

    def read_chunk(self, timeout=1.0):
        """
        Read audio chunk from queue

        Args:
            timeout: Timeout in seconds

        Returns:
            numpy array of audio data (float32) or None if timeout
        """
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def read_all(self):
        """
        Read all available audio chunks

        Returns:
            List of numpy arrays
        """
        chunks = []
        while not self.audio_queue.empty():
            try:
                chunks.append(self.audio_queue.get_nowait())
            except queue.Empty:
                break
        return chunks

    def get_audio_buffer(self, duration_seconds=None):
        """
        Get audio buffer for specified duration or all available

        Args:
            duration_seconds: Duration in seconds, None for all available

        Returns:
            Concatenated numpy array of audio data
        """
        chunks = []

        if duration_seconds is None:
            # Get all available
            chunks = self.read_all()
        else:
            # Calculate number of chunks needed
            frames_needed = int(self.sample_rate * duration_seconds)
            frames_per_chunk = self.chunk_size
            chunks_needed = int(np.ceil(frames_needed / frames_per_chunk))

            for _ in range(chunks_needed):
                chunk = self.read_chunk(timeout=0.1)
                if chunk is not None:
                    chunks.append(chunk)
                else:
                    break

        if not chunks:
            return np.array([], dtype=np.float32)

        # Concatenate all chunks
        audio_data = np.concatenate(chunks, axis=0)

        # Flatten if stereo
        if audio_data.ndim > 1:
            audio_data = audio_data.mean(axis=1)

        return audio_data

    def clear_buffer(self):
        """Clear the audio queue"""
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        logger.debug("🧹 Audio buffer cleared")

    def __del__(self):
        """Cleanup on deletion"""
        self.stop_recording()


# Convenience function for quick audio recording
def record_audio(duration_seconds, sample_rate=16000):
    """
    Quick function to record audio for a fixed duration

    Args:
        duration_seconds: How long to record
        sample_rate: Sample rate (default 16000 for Whisper)

    Returns:
        numpy array of audio data
    """
    logger.info(f"🎙️ Recording for {duration_seconds} seconds...")

    audio = sd.rec(
        int(duration_seconds * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype=np.float32
    )
    sd.wait()  # Wait for recording to complete

    logger.info("✅ Recording complete")
    return audio.flatten()


if __name__ == "__main__":
    # Test audio capture
    logger.info("Testing AudioCapture...")

    capture = AudioCapture(sample_rate=16000)

    logger.info("Recording for 3 seconds...")
    capture.start_recording()

    import time
    time.sleep(3)

    audio_data = capture.get_audio_buffer()
    capture.stop_recording()

    logger.info(f"Captured {len(audio_data)} samples ({len(audio_data)/16000:.2f} seconds)")
    logger.info("✅ AudioCapture test complete!")