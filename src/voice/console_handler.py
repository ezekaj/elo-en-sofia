"""
Console Mode Handler - Terminal-based voice interaction

Uses PyAudio for microphone input and speaker output.
Implements proper audio device management to avoid conflicts.
"""
import pyaudio
import wave
import io
import sys
import time
import numpy as np
from ..agent.sofia_local import SofiaLocalAgent


class ConsoleVoiceHandler:
    """
    Handles voice interaction in console/terminal mode

    Manages audio recording, playback, and proper device cleanup
    """

    def __init__(self):
        """Initialize audio system"""
        # Audio configuration
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.CHUNK = 1024
        self.RECORD_SECONDS = 5  # Maximum recording time

        self.audio = None
        self.stream = None

        print("\n" + "=" * 60)
        print("🎙️  SOFIA - CONSOLE MODE")
        print("=" * 60)

    def initialize_audio(self):
        """Initialize PyAudio system"""
        try:
            self.audio = pyaudio.PyAudio()
            print("✅ Audio system initialized")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize audio system: {e}")
            return False

    def cleanup_audio(self):
        """Cleanup audio resources"""
        if self.stream:
            try:
                if self.stream.is_active():
                    self.stream.stop_stream()
                self.stream.close()
            except:
                pass
            self.stream = None

        if self.audio:
            try:
                self.audio.terminate()
            except:
                pass
            self.audio = None

    def record_audio(self) -> bytes:
        """
        Record audio from microphone

        Returns:
            bytes: Recorded audio data
        """
        print("\n🎤 Listening... (speak now, press Ctrl+C when done)")

        try:
            # Open stream for recording
            stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )

            frames = []
            start_time = time.time()

            try:
                while time.time() - start_time < self.RECORD_SECONDS:
                    try:
                        data = stream.read(self.CHUNK, exception_on_overflow=False)
                        frames.append(data)
                    except KeyboardInterrupt:
                        print("\n✋ Recording stopped")
                        break
            finally:
                # Always cleanup stream
                stream.stop_stream()
                stream.close()

            if not frames:
                return None

            # Convert to audio data
            audio_data = b''.join(frames)
            return audio_data

        except Exception as e:
            print(f"❌ Recording error: {e}")
            return None

    def play_audio(self, audio_chunks):
        """
        Play audio through speakers

        Args:
            audio_chunks: Iterator of audio chunks
        """
        print("🔊 Speaking...")

        try:
            # Collect all chunks first
            all_audio = b''.join(audio_chunks)

            if not all_audio:
                return

            # Open stream for playback
            stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                output=True,
                frames_per_buffer=self.CHUNK
            )

            # Play audio
            stream.write(all_audio)

            # Cleanup
            stream.stop_stream()
            stream.close()

        except Exception as e:
            print(f"❌ Playback error: {e}")

    def run(self):
        """Run console voice interaction loop"""
        if not self.initialize_audio():
            print("❌ Cannot start console mode - audio initialization failed")
            return

        try:
            # Initialize Sofia
            sofia = SofiaLocalAgent()

            # Print initial greeting
            print(f"\n🤖 Sofia: {sofia.get_initial_greeting()}\n")

            # Speak initial greeting
            print("🔊 Speaking initial greeting...")
            greeting_audio = list(sofia.tts.synthesize(sofia.get_initial_greeting()))
            self.play_audio(iter(greeting_audio))

            print("\n" + "=" * 60)
            print("💬 CONVERSATION STARTED")
            print("=" * 60)
            print("Instructions:")
            print("  - Speak after you see '🎤 Listening...'")
            print("  - Press Ctrl+C to stop speaking")
            print("  - Say 'goodbye' to end conversation")
            print("  - Press Ctrl+C twice to force quit")
            print("=" * 60 + "\n")

            # Main conversation loop
            while not sofia.is_conversation_ended():
                try:
                    # Record user input
                    audio_data = self.record_audio()

                    if audio_data is None or len(audio_data) == 0:
                        print("⚠️  No audio recorded, try again")
                        continue

                    # Process with Sofia
                    response_audio = list(sofia.process_audio(audio_data))

                    # Play response
                    if response_audio:
                        self.play_audio(iter(response_audio))

                    # Small pause between turns
                    time.sleep(0.5)

                except KeyboardInterrupt:
                    print("\n\n⚠️  Interrupted - press Ctrl+C again to quit, or wait to continue...")
                    time.sleep(2)
                    continue

            print("\n" + "=" * 60)
            print("👋 CONVERSATION ENDED")
            print("=" * 60)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Shutting down...")

        except Exception as e:
            print(f"\n❌ Error: {e}")

        finally:
            self.cleanup_audio()
            print("✅ Audio system cleaned up")


def run_console_mode():
    """Entry point for console mode"""
    handler = ConsoleVoiceHandler()
    handler.run()