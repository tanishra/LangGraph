from typing import List, Optional, Any
import requests

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)
from langchain_core.outputs import ChatGeneration, ChatResult


class EuriChatModel(BaseChatModel):
    """
    LangChain custom chat model wrapper for EURI API
    """

    api_key: str
    model: str = "gpt-4.1-mini"
    temperature: float = 0.7
    max_tokens: int = 1000
    base_url: str = "https://api.euron.one/api/v1/euri/chat/completions"

    @property
    def _llm_type(self) -> str:
        return "euri-chat"

    def _convert_messages_to_euri(
        self, messages: List[BaseMessage]
    ) -> List[dict]:
        """
        Convert LangChain messages → EURI/OpenAI-style messages
        """
        euri_messages = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = "user"
                content = msg.content
            elif isinstance(msg, AIMessage):
                role = "assistant"
                content = msg.content
            elif isinstance(msg, SystemMessage):
                role = "system"
                content = msg.content
            else:
                raise ValueError(f"Unsupported message type: {type(msg)}")

            # EURI supports assistant content as structured text
            if role == "assistant":
                euri_messages.append(
                    {
                        "role": role,
                        "content": [
                            {
                                "type": "text",
                                "text": content,
                            }
                        ],
                    }
                )
            else:
                euri_messages.append(
                    {
                        "role": role,
                        "content": content,
                    }
                )

        return euri_messages

    def _generate(self, messages, stop=None, **kwargs):
        payload = {
            "model": self.model,
            "messages": self._convert_messages_to_euri(messages),
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        response = requests.post(
            self.base_url,
            json=payload,
            headers=headers,
            timeout=60,
        )
        
        response.raise_for_status()
        data = response.json()

        message_content = data["choices"][0]["message"]["content"]

        # Handle both response formats
        if isinstance(message_content, list):
            assistant_text = message_content[0]["text"]
        else:
            assistant_text = message_content

        ai_message = AIMessage(content=assistant_text)
        generation = ChatGeneration(message=ai_message)

        return ChatResult(generations=[generation])