from typing import List, Optional, Iterator
import requests

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
    AIMessageChunk
)
from langchain_core.outputs import ChatGeneration, ChatResult, ChatGenerationChunk
import json


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
    
    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs,
    ):
        payload = {
            "model": self.model,
            "messages": self._convert_messages_to_euri(messages),
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stream": True,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        with requests.post(
            self.base_url,
            json=payload,
            headers=headers,
            stream=True,
            timeout=60,
        ) as response:
            response.raise_for_status()
            
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                
                # Handle SSE format
                if line.startswith("data:"):
                    line = line[len("data:"):].strip()

                if line == "[DONE]":
                    break

                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue

                choices = chunk.get("choices")
                if not choices:
                    continue  

                delta = choices[0].get("delta", {})
                content = delta.get("content")

                if not content:
                    continue

                yield ChatGenerationChunk(
                    message=AIMessageChunk(content=content)
                )


# from dotenv import load_dotenv

# load_dotenv()
# import os
# api = os.getenv("EURI_API_KEY")

# llm = EuriChatModel(api_key=api,model='gpt-4.1-mini')

# for chunk in llm.stream("what is the recipe of pasta"):
#     print(chunk.content, end="", flush=True)
