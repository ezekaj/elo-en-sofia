"""
Gradio Web Interface for Sofia
Simplified, Windows-optimized web UI without WebRTC complexity
"""
import gradio as gr
import numpy as np
from loguru import logger
from pathlib import Path

from ..audio.capture import AudioCapture
from ..audio.playback import AudioPlayback
from ..audio.vad import VoiceActivityDetector
from ..stt.whisper_engine import WhisperSTT
from ..tts_new.kokoro_engine import KokoroTTS
from ..llm.ollama_client import OllamaClient
from ..agent.prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION


class GradioInterface:
    """
    Gradio-based web interface for Sofia

    Features:
    - Audio recording and playback
    - Speech-to-text processing
    - LLM conversation
    - Text-to-speech output
    - Visual feedback
    """

    def __init__(self):
        """Initialize Gradio interface"""
        logger.info("🌐 Initializing Gradio interface...")

        # Initialize components
        self.stt = WhisperSTT(model_size='tiny.en')
        self.tts = KokoroTTS(voice='af_bella', speed=1.0)
        self.llm = OllamaClient(model='gemma3:4b')
        self.playback = AudioPlayback(sample_rate=24000)

        # Conversation state
        self.conversation_active = False

        logger.info("✅ Gradio interface initialized")

    def process_audio(self, audio_data):
        """
        Process audio input from Gradio

        Args:
            audio_data: Tuple of (sample_rate, audio_array) from Gradio

        Returns:
            Tuple of (response_text, response_audio)
        """
        try:
            if audio_data is None:
                return "No audio recorded", None

            sample_rate, audio_array = audio_data

            # Convert to float32 if needed
            if audio_array.dtype == np.int16:
                audio_array = audio_array.astype(np.float32) / 32768.0

            logger.info(f"🎤 Processing audio: {len(audio_array)} samples at {sample_rate}Hz")

            # Transcribe speech
            logger.info("📝 Transcribing...")
            transcription = self.stt.transcribe(audio_array, sample_rate)

            if not transcription:
                return "No speech detected", None

            logger.info(f"📝 Transcribed: '{transcription}'")

            # Generate LLM response
            logger.info("🤖 Generating response...")
            if not self.conversation_active:
                # Start conversation
                full_prompt = AGENT_INSTRUCTION + "\n\n" + SESSION_INSTRUCTION
                self.llm.start_conversation(full_prompt)
                self.conversation_active = True

            response_text = self.llm.generate_response(transcription)
            logger.info(f"🤖 Response: '{response_text}'")

            # Generate speech
            logger.info("🔊 Synthesizing speech...")
            tts_sample_rate, response_audio = self.tts.synthesize(response_text)

            # Convert to format Gradio expects (sample_rate, numpy array)
            response_audio_data = (tts_sample_rate, response_audio)

            logger.info("✅ Processing complete")
            return response_text, response_audio_data

        except Exception as e:
            logger.error(f"❌ Error processing audio: {e}")
            import traceback
            traceback.print_exc()
            return f"Error: {str(e)}", None

    def reset_conversation(self):
        """Reset the conversation"""
        self.llm.reset_conversation()
        self.conversation_active = False
        return "Conversation reset"

    def create_interface(self):
        """Create and configure Gradio interface"""

        with gr.Blocks(title="Sofia - Voice AI Assistant") as interface:
            gr.Markdown("""
            # 🎙️ Sofia - Windows-Native Voice AI Assistant

            **100% Local • No Cloud • Privacy-First**

            Click the microphone to record your voice, then click again to stop.
            Sofia will transcribe, process, and respond with voice!
            """)

            with gr.Row():
                with gr.Column():
                    audio_input = gr.Audio(
                        sources=["microphone"],
                        type="numpy",
                        label="🎤 Speak to Sofia",
                        streaming=False
                    )

                    with gr.Row():
                        submit_btn = gr.Button("💬 Send", variant="primary")
                        reset_btn = gr.Button("🔄 Reset Conversation")

                with gr.Column():
                    text_output = gr.Textbox(
                        label="📝 Sofia's Response (Text)",
                        lines=5,
                        interactive=False
                    )

                    audio_output = gr.Audio(
                        label="🔊 Sofia's Response (Voice)",
                        type="numpy",
                        autoplay=True
                    )

            # Info section
            with gr.Accordion("ℹ️ How to Use", open=False):
                gr.Markdown("""
                ### Instructions:
                1. **Click the microphone** button to start recording
                2. **Speak clearly** your message to Sofia
                3. **Click the microphone** again to stop recording
                4. **Click "Send"** to process your message
                5. Sofia will respond with both text and voice!

                ### Tips:
                - Speak in a quiet environment for best results
                - Wait for Sofia's response before speaking again
                - Say "goodbye" to end the conversation politely
                - Click "Reset Conversation" to start over

                ### Technology:
                - **STT:** faster-whisper (tiny.en model)
                - **LLM:** Ollama (gemma3:4b)
                - **TTS:** Kokoro ONNX (high-quality neural voice)
                - **Audio:** Windows-native sounddevice
                """)

            # Connect events
            submit_btn.click(
                fn=self.process_audio,
                inputs=[audio_input],
                outputs=[text_output, audio_output]
            )

            reset_btn.click(
                fn=self.reset_conversation,
                inputs=[],
                outputs=[text_output]
            )

        return interface

    def launch(self, share=False, port=7860):
        """
        Launch Gradio interface

        Args:
            share: Create public sharing link
            port: Port to run on (default: 7860)
        """
        logger.info(f"🚀 Launching Gradio interface on port {port}...")

        interface = self.create_interface()

        interface.launch(
            server_name="0.0.0.0",
            server_port=port,
            share=share,
            inbrowser=True  # Open in browser automatically
        )


def main():
    """Main entry point for Gradio interface"""
    logger.info("=" * 60)
    logger.info("  SOFIA - Voice AI Assistant (Gradio Web UI)")
    logger.info("=" * 60)

    try:
        app = GradioInterface()
        app.launch()
    except KeyboardInterrupt:
        logger.info("\n👋 Goodbye!")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()