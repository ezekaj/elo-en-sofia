"""
Browser Mode Handler - Web-based voice interaction using FastRTC

Uses FastRTC Stream with Gradio UI for browser-based voice interaction.
"""
from fastrtc import ReplyOnPause, Stream
from ..agent.sofia_local import SofiaLocalAgent


class BrowserVoiceHandler:
    """
    Handles voice interaction in browser mode using FastRTC
    """

    def __init__(self):
        """Initialize browser handler"""
        print("\n" + "=" * 60)
        print("🌐 SOFIA - BROWSER MODE (FastRTC)")
        print("=" * 60)

        # Initialize Sofia agent
        self.sofia = SofiaLocalAgent()

        print("✅ Browser handler initialized")
        print("=" * 60 + "\n")

    def voice_handler(self, audio):
        """
        Handle voice interaction (called by FastRTC)

        Args:
            audio: Audio data from browser

        Yields:
            Audio chunks for playback
        """
        try:
            # Process audio with Sofia
            for audio_chunk in self.sofia.process_audio(audio):
                yield audio_chunk

            # Check if conversation should end
            if self.sofia.is_conversation_ended():
                print("\n👋 Conversation ended by user")

        except Exception as e:
            print(f"❌ Error in voice handler: {e}")
            # Return error message
            error_msg = "I apologize, but I encountered an error."
            for audio_chunk in self.sofia.tts.synthesize(error_msg):
                yield audio_chunk

    def run(self):
        """Run browser mode with FastRTC Gradio UI"""
        try:
            print("🌐 Starting Gradio UI...")
            print("📱 Your browser will open automatically")
            print("🎙️  Click the microphone button to start talking")
            print("\n⚠️  IMPORTANT: If you see 'NotFoundError: Requested device not found':")
            print("   1. Check System Settings → Privacy → Microphone")
            print("   2. Enable microphone for your browser")
            print("   3. Restart browser and try again")
            print("   4. Or use console mode: ./run_console.sh")
            print("=" * 60 + "\n")

            # Create FastRTC Stream
            stream = Stream(
                ReplyOnPause(self.voice_handler),
                modality="audio",
                mode="send-receive"
            )

            # Launch Gradio UI (opens browser)
            stream.ui.launch()

        except KeyboardInterrupt:
            print("\n\n👋 Shutting down browser mode...")
        except Exception as e:
            print(f"\n❌ Browser mode error: {e}")
            print("\n💡 TIP: Try console mode instead: ./run_console.sh")


def run_browser_mode():
    """Entry point for browser mode"""
    handler = BrowserVoiceHandler()
    handler.run()