"""
LLM Module using Ollama
Handles conversation with local LLM
"""
import ollama
import json
from typing import List, Dict, Any, Optional


class LocalLLM:
    def __init__(self, model: str = "gemma3:4b", system_prompt: str = ""):
        """
        Initialize Ollama LLM client

        Args:
            model (str): Ollama model to use
            system_prompt (str): System prompt for the agent
        """
        self.model = model
        self.system_prompt = system_prompt
        self.conversation_history = []

        print(f"🤖 Initializing Ollama with model: {model}")

        # Test connection
        try:
            ollama.list()
            print("✅ Ollama connection successful")
        except Exception as e:
            print(f"❌ Ollama connection failed: {e}")
            print("⚠️  Make sure Ollama is running: ollama serve")
            raise

    def chat(self, user_message: str, tools: Optional[List[Dict]] = None) -> str:
        """
        Send message to LLM and get response

        Args:
            user_message (str): User's message
            tools (List[Dict], optional): Available tools for function calling

        Returns:
            str: LLM response
        """
        # Build messages
        messages = []

        # Add system prompt
        if self.system_prompt:
            messages.append({
                "role": "system",
                "content": self.system_prompt
            })

        # Add conversation history
        messages.extend(self.conversation_history)

        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })

        try:
            # Call Ollama
            response = ollama.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": 0.7,
                    "num_predict": 200,  # Limit response length for voice
                }
            )

            assistant_message = response["message"]["content"]

            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})

            # Keep only last 10 messages to avoid context overflow
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]

            return assistant_message

        except Exception as e:
            print(f"❌ LLM Error: {e}")
            return "I apologize, but I'm having trouble processing that right now."

    def chat_with_tools(self, user_message: str, available_tools: Dict[str, Any]) -> tuple[str, Optional[str], Optional[Dict]]:
        """
        Chat with tool calling support

        Args:
            user_message (str): User's message
            available_tools (Dict): Dictionary of available tool functions

        Returns:
            tuple: (response_text, tool_name, tool_result)
        """
        # First, check if user message requires a tool
        # For now, simple keyword matching (can be enhanced with function calling)

        # Get base response
        response = self.chat(user_message)

        # Simple tool detection (you can enhance this)
        tool_called = None
        tool_result = None

        # Example: Check if response needs time info
        if any(keyword in user_message.lower() for keyword in ["time", "date", "today", "now"]):
            if "get_current_datetime_info" in available_tools:
                tool_called = "get_current_datetime_info"
                tool_result = available_tools[tool_called]()

        return response, tool_called, tool_result

    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
        print("🔄 Conversation history cleared")