"""
Console Interface for Sofia
Terminal-based voice interaction
"""
import time
from loguru import logger

from ..audio.capture import AudioCapture
from ..audio.playback import AudioPlayback
from ..audio.vad import SpeechDetector
from ..stt.whisper_engine import WhisperSTT
from ..tts_new.kokoro_engine import KokoroTTS
from ..llm.ollama_client import OllamaClient
from ..agent.prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION


class ConsoleInterface:
    """
    Console-based interface for Sofia

    Features:
    - Voice recording with VAD
    - Speech-to-text
    - LLM conversation
    - Text-to-speech playback
    - Simple terminal UI
    """

    def __init__(self):
        """Initialize console interface"""
        logger.info("🖥️ Initializing console interface...")

        # Initialize components
        self.capture = AudioCapture(sample_rate=16000)
        self.playback = AudioPlayback(sample_rate=24000)
        self.vad = SpeechDetector(sample_rate=16000, aggressiveness=2)
        self.stt = WhisperSTT(model_size='tiny.en')
        self.tts = KokoroTTS(voice='af_bella', speed=1.0)
        self.llm = OllamaClient(model='gemma3:4b')

        logger.info("✅ Console interface initialized")

    def record_with_vad(self, max_duration=10):
        """
        Record audio with voice activity detection

        Args:
            max_duration: Maximum recording duration in seconds

        Returns:
            Audio data as numpy array
        """
        print("\n🎤 Listening... (Speak now, or press Ctrl+C to stop)")

        self.capture.start_recording()
        self.vad.reset()

        audio_chunks = []
        start_time = time.time()
        speech_detected = False
        silence_duration = 0
        max_silence = 2.0  # Stop after 2 seconds of silence

        try:
            while True:
                # Check timeout
                if time.time() - start_time > max_duration:
                    print("⏱️ Maximum duration reached")
                    break

                # Read audio chunk
                chunk = self.capture.read_chunk(timeout=0.1)
                if chunk is None:
                    continue

                audio_chunks.append(chunk)

                # Check for speech
                is_speaking, state_changed = self.vad.process_frame(chunk)

                if state_changed:
                    if is_speaking:
                        print("🗣️ Speech detected...")
                        speech_detected = True
                        silence_duration = 0
                    else:
                        print("🤐 Speech ended")

                # Track silence
                if speech_detected and not is_speaking:
                    silence_duration += 0.1

                    if silence_duration >= max_silence:
                        print("✅ Recording complete")
                        break

        except KeyboardInterrupt:
            print("\n⏹️ Recording stopped by user")

        finally:
            self.capture.stop_recording()

        # Combine chunks
        if audio_chunks:
            import numpy as np
            audio_data = np.concatenate(audio_chunks, axis=0)
            if audio_data.ndim > 1:
                audio_data = audio_data.mean(axis=1)
            return audio_data
        else:
            return None

    def record_simple(self, duration=5):
        """
        Simple fixed-duration recording

        Args:
            duration: Recording duration in seconds

        Returns:
            Audio data
        """
        print(f"\n🎤 Recording for {duration} seconds...")
        print("Speak now!")

        self.capture.start_recording()
        time.sleep(duration)
        audio_data = self.capture.get_audio_buffer()
        self.capture.stop_recording()

        print("✅ Recording complete")
        return audio_data

    def speak(self, text):
        """
        Speak text using TTS

        Args:
            text: Text to speak
        """
        print(f"\n🔊 Sofia: {text}")

        # Synthesize speech
        sample_rate, audio = self.tts.synthesize(text)

        # Play audio
        self.playback.play(audio, blocking=True)

    def run(self):
        """Run the console interface"""
        print("\n" + "=" * 60)
        print("  SOFIA - Voice AI Assistant (Console Mode)")
        print("=" * 60)
        print("\nInitializing...")

        # Start conversation
        full_prompt = AGENT_INSTRUCTION + "\n\n" + SESSION_INSTRUCTION
        initial_greeting = self.llm.start_conversation(full_prompt)

        # Speak greeting
        self.speak(initial_greeting)

        print("\n" + "=" * 60)
        print("Ready! Say something to Sofia.")
        print("Say 'goodbye' to end the conversation.")
        print("Press Ctrl+C anytime to exit.")
        print("=" * 60)

        conversation_active = True

        while conversation_active:
            try:
                # Record user speech
                print("\n" + "-" * 60)
                audio_data = self.record_with_vad(max_duration=15)

                if audio_data is None or len(audio_data) == 0:
                    print("⚠️ No audio recorded. Please try again.")
                    continue

                # Transcribe
                print("\n📝 Transcribing...")
                transcription = self.stt.transcribe(audio_data, sample_rate=16000)

                if not transcription:
                    print("⚠️ No speech detected. Please try again.")
                    continue

                print(f"You said: \"{transcription}\"")

                # Check for goodbye
                if 'goodbye' in transcription.lower() or 'bye' in transcription.lower():
                    print("\n👋 Ending conversation...")
                    response = self.llm.generate_response(transcription)
                    self.speak(response)
                    conversation_active = False
                    break

                # Generate response
                print("\n🤖 Thinking...")
                response = self.llm.generate_response(transcription)

                # Speak response
                self.speak(response)

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                conversation_active = False
                break

            except Exception as e:
                logger.error(f"❌ Error: {e}")
                print(f"\n⚠️ Error: {e}")
                print("Let's try again...")

        print("\n" + "=" * 60)
        print("Thank you for using Sofia!")
        print("=" * 60)


def main():
    """Main entry point for console interface"""
    try:
        interface = ConsoleInterface()
        interface.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()