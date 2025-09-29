"""
Sofia Local Agent - Local Voice AI Agent

Integrates STT, TTS, LLM, and Sofia's tools for local voice interaction.
"""
from ..voice.stt import SpeechToText
from ..voice.tts import TextToSpeech
from ..voice.llm import LocalLLM
from .tools_local import AVAILABLE_TOOLS, get_time_based_greeting, get_current_datetime_info
from .prompts import AGENT_INSTRUCTION
import re


class SofiaLocalAgent:
    """
    Sofia Local Agent - 100% local voice AI assistant

    Combines:
    - Moonshine STT (Speech-to-Text)
    - Kokoro TTS (Text-to-Speech)
    - Ollama LLM (Language Model)
    - Sofia's tools and personality
    """

    def __init__(self, model: str = "gemma3:4b"):
        """
        Initialize Sofia Local Agent

        Args:
            model (str): Ollama model to use (default: gemma3:4b)
        """
        print("\n" + "=" * 60)
        print("🤖 SOFIA LOCAL AGENT - Initializing...")
        print("=" * 60)

        # Initialize voice components
        self.stt = SpeechToText()
        self.tts = TextToSpeech()

        # Initialize LLM with Sofia's personality
        self.llm = LocalLLM(
            model=model,
            system_prompt=self._get_enhanced_system_prompt()
        )

        # Track conversation state
        self.should_end_conversation = False
        self.conversation_count = 0

        # Initial greeting
        self._generate_initial_greeting()

        print("=" * 60)
        print("✅ Sofia is ready to assist!")
        print("=" * 60 + "\n")

    def _get_enhanced_system_prompt(self) -> str:
        """
        Get enhanced system prompt with tool information

        Returns:
            str: Enhanced system prompt
        """
        # Get current time context for greeting
        time_info = get_current_datetime_info()
        greeting_info = get_time_based_greeting()

        time_context = ""
        if time_info["status"] == "success":
            dt = time_info["datetime_info"]
            time_context = f"\n\n**CURRENT CONTEXT**: It is {dt['current_time']} on {dt['current_date']} ({dt['time_period']})."

        if greeting_info["status"] == "success":
            time_context += f"\nUse '{greeting_info['greeting_info']['greeting']}' for your greeting."

        return AGENT_INSTRUCTION + time_context + """

**IMPORTANT**: Since you are running locally with Ollama, you don't have direct access to tools/functions.
However, when appropriate:
- Provide time/date information using your knowledge of current context
- Be helpful and informative
- Keep responses concise and natural for voice interaction
- Avoid emojis and special characters (your output will be spoken)
- Keep responses under 200 words for better voice experience
"""

    def _generate_initial_greeting(self):
        """Generate and store initial greeting"""
        greeting_info = get_time_based_greeting()
        if greeting_info["status"] == "success":
            self.initial_greeting = greeting_info["greeting_info"]["full_greeting"]
        else:
            self.initial_greeting = "Hello! I'm Sofia, your AI voice assistant. How can I help you today?"

    def get_initial_greeting(self) -> str:
        """
        Get the initial greeting text

        Returns:
            str: Initial greeting message
        """
        return self.initial_greeting

    def process_audio(self, audio_data):
        """
        Process audio input and generate audio response

        Args:
            audio_data: Audio data from microphone

        Yields:
            Audio chunks for playback
        """
        try:
            # 1. Speech-to-Text
            print("🎤 Listening...")
            transcript = self.stt.transcribe(audio_data)

            if not transcript or transcript.strip() == "":
                print("⚠️  No speech detected")
                return

            print(f"👤 User: {transcript}")

            # 2. Check for conversation end keywords
            if self._should_end_conversation(transcript):
                self.should_end_conversation = True
                response_text = "Thank you for speaking with me today. Have a great day! Goodbye!"
            else:
                # 3. Get LLM response
                response_text = self.llm.chat(transcript)

                # Check if response contains end signal
                if "*[CALL_END_SIGNAL]*" in response_text:
                    self.should_end_conversation = True
                    response_text = response_text.replace("*[CALL_END_SIGNAL]*", "")

            print(f"🤖 Sofia: {response_text}")

            # 4. Text-to-Speech
            print("🔊 Speaking...")
            for audio_chunk in self.tts.synthesize(response_text):
                yield audio_chunk

            self.conversation_count += 1

        except Exception as e:
            print(f"❌ Error processing audio: {e}")
            error_message = "I apologize, but I encountered an error. Please try again."
            for audio_chunk in self.tts.synthesize(error_message):
                yield audio_chunk

    def process_text(self, text: str) -> str:
        """
        Process text input and return text response (for dev mode)

        Args:
            text (str): User's text input

        Returns:
            str: Sofia's text response
        """
        try:
            print(f"👤 User: {text}")

            # Check for conversation end
            if self._should_end_conversation(text):
                self.should_end_conversation = True
                response_text = "Thank you for speaking with me today. Have a great day! Goodbye!"
            else:
                # Get LLM response
                response_text = self.llm.chat(text)

                # Check if response contains end signal
                if "*[CALL_END_SIGNAL]*" in response_text:
                    self.should_end_conversation = True
                    response_text = response_text.replace("*[CALL_END_SIGNAL]*", "")

            print(f"🤖 Sofia: {response_text}")
            self.conversation_count += 1

            return response_text

        except Exception as e:
            print(f"❌ Error processing text: {e}")
            return "I apologize, but I encountered an error. Please try again."

    def _should_end_conversation(self, text: str) -> bool:
        """
        Check if conversation should end based on user input

        Args:
            text (str): User's input text

        Returns:
            bool: True if conversation should end
        """
        end_keywords = [
            "goodbye", "bye", "see you", "thanks bye", "that's all",
            "end conversation", "stop", "quit", "exit"
        ]

        text_lower = text.lower()
        return any(keyword in text_lower for keyword in end_keywords)

    def is_conversation_ended(self) -> bool:
        """
        Check if conversation has ended

        Returns:
            bool: True if conversation should end
        """
        return self.should_end_conversation

    def reset_conversation(self):
        """Reset conversation state"""
        self.llm.reset_conversation()
        self.should_end_conversation = False
        self.conversation_count = 0
        print("🔄 Conversation reset")