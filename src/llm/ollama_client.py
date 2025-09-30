"""
Ollama LLM Client with Sofia Integration
Handles conversation with Ollama and tool execution
"""
import ollama
import json
from loguru import logger
from typing import List, Dict, Any, Optional
from ..agent.tools_local import AVAILABLE_TOOLS


class OllamaClient:
    """
    Ollama LLM client with tool support for Sofia

    Features:
    - Conversation with Ollama models
    - Tool execution support
    - Context management
    - Error handling
    """

    def __init__(self, model='gemma3:4b', host='http://localhost:11434'):
        """
        Initialize Ollama client

        Args:
            model: Ollama model name (default: gemma3:4b)
            host: Ollama server URL
        """
        self.model = model
        self.host = host
        self.conversation_history = []
        self.tools = AVAILABLE_TOOLS

        logger.info(f"🤖 Initializing Ollama client: {model}")
        self._verify_connection()

    def _verify_connection(self):
        """Verify connection to Ollama"""
        try:
            # Check if Ollama is running
            response = ollama.list()
            # Handle both dict response (old) and Pydantic model (new)
            if hasattr(response, 'models'):
                models_list = response.models
            else:
                models_list = response.get('models', [])

            logger.info(f"✅ Connected to Ollama, {len(models_list)} models available")

            # Check if our model exists
            model_exists = any(
                (m.model if hasattr(m, 'model') else m['model']).startswith(self.model.split(':')[0])
                for m in models_list
            )

            if not model_exists:
                logger.warning(f"⚠️ Model {self.model} not found. Available models:")
                for m in models_list:
                    model_name = m.model if hasattr(m, 'model') else m['model']
                    logger.info(f"  - {model_name}")
                raise ValueError(f"Model {self.model} not found. Run: ollama pull {self.model}")

            logger.info(f"✅ Model {self.model} is ready")

        except Exception as e:
            logger.error(f"❌ Failed to connect to Ollama: {e}")
            logger.error("Make sure Ollama is running: ollama serve")
            raise

    def add_system_message(self, content: str):
        """Add system message to conversation"""
        self.conversation_history.append({
            'role': 'system',
            'content': content
        })

    def add_user_message(self, content: str):
        """Add user message to conversation"""
        self.conversation_history.append({
            'role': 'user',
            'content': content
        })

    def add_assistant_message(self, content: str):
        """Add assistant message to conversation"""
        self.conversation_history.append({
            'role': 'assistant',
            'content': content
        })

    def execute_tool(self, tool_name: str, tool_args: Dict = None) -> Optional[Dict]:
        """
        Execute a tool by name

        Args:
            tool_name: Name of tool to execute
            tool_args: Arguments for tool (if any)

        Returns:
            Tool execution result or None
        """
        try:
            if tool_name not in self.tools:
                logger.warning(f"Unknown tool: {tool_name}")
                return None

            tool_func = self.tools[tool_name]

            # Execute tool
            if tool_args:
                result = tool_func(**tool_args)
            else:
                result = tool_func()

            logger.debug(f"✅ Tool executed: {tool_name}")
            return result

        except Exception as e:
            logger.error(f"❌ Tool execution error ({tool_name}): {e}")
            return {'status': 'error', 'error': str(e)}

    def generate_response(self, user_message: str, stream: bool = False) -> str:
        """
        Generate response from Ollama

        Args:
            user_message: User's message
            stream: Whether to stream response (not implemented yet)

        Returns:
            Assistant's response
        """
        try:
            # Add user message to history
            self.add_user_message(user_message)

            # Generate response
            logger.debug(f"💬 Generating response for: '{user_message[:50]}...'")

            response = ollama.chat(
                model=self.model,
                messages=self.conversation_history
            )

            assistant_message = response['message']['content']

            # Check for tool usage patterns
            # Simple pattern matching for tool calls
            assistant_message = self._process_tool_calls(assistant_message)

            # Add to history
            self.add_assistant_message(assistant_message)

            logger.debug(f"✅ Response generated: '{assistant_message[:50]}...'")
            return assistant_message

        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")
            return "I apologize, but I encountered an error processing your request."

    def _process_tool_calls(self, message: str) -> str:
        """
        Process tool calls in assistant message
        Simple implementation for now - can be enhanced later

        Args:
            message: Assistant's message

        Returns:
            Processed message with tool results
        """
        # Check for tool invocation patterns
        # This is a simple implementation - can be made more sophisticated

        # Check for end conversation signal
        if 'end_conversation' in message.lower() or '*[call_end_signal]*' in message.lower():
            result = self.execute_tool('end_conversation')
            if result:
                return result.get('message', message)

        return message

    def start_conversation(self, system_prompt: str) -> str:
        """
        Start a new conversation with system prompt

        Args:
            system_prompt: System instructions for the conversation

        Returns:
            Initial greeting from assistant
        """
        try:
            # Clear history
            self.conversation_history = []

            # Add system prompt
            self.add_system_message(system_prompt)

            # Get time-based greeting
            greeting_info = self.execute_tool('get_time_based_greeting')
            datetime_info = self.execute_tool('get_current_datetime_info')

            if greeting_info and datetime_info:
                # Create context-aware greeting
                greeting = greeting_info['greeting_info']['full_greeting']
                time_context = datetime_info['datetime_info']['context']

                initial_prompt = f"Start the conversation. {time_context}. Greet the user appropriately."
                self.add_user_message(initial_prompt)

                # Generate personalized greeting
                response = ollama.chat(
                    model=self.model,
                    messages=self.conversation_history
                )

                assistant_message = response['message']['content']
                self.add_assistant_message(assistant_message)

                return assistant_message
            else:
                # Fallback greeting
                return "Hello! I'm Sofia, your AI voice assistant. How can I help you today?"

        except Exception as e:
            logger.error(f"❌ Error starting conversation: {e}")
            return "Hello! I'm Sofia. How can I help you?"

    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
        logger.info("🔄 Conversation reset")

    def get_conversation_length(self) -> int:
        """Get number of messages in conversation"""
        return len(self.conversation_history)


if __name__ == "__main__":
    # Test Ollama client
    logger.info("Testing OllamaClient...")

    try:
        client = OllamaClient(model='gemma3:4b')

        # Test tool execution
        logger.info("\nTesting tool execution...")
        greeting = client.execute_tool('get_time_based_greeting')
        logger.info(f"Greeting: {greeting}")

        # Test conversation
        logger.info("\nTesting conversation...")
        from ..agent.prompts import AGENT_INSTRUCTION

        initial_greeting = client.start_conversation(AGENT_INSTRUCTION)
        logger.info(f"Initial greeting: {initial_greeting}")

        # Test user interaction
        response = client.generate_response("What time is it?")
        logger.info(f"Response: {response}")

        logger.info("\n✅ OllamaClient test complete!")

    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()