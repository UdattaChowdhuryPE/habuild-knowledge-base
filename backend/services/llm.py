import os
from anthropic import Anthropic
from typing import Generator, List, Dict, Any


class LLMService:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = Anthropic(api_key=api_key)

    def stream_chat(
        self,
        question: str,
        context: str,
        conversation_history: List[Dict[str, str]]
    ) -> Generator[str, None, None]:
        """
        Stream a response from Claude using conversation history and retrieved context.
        Yields tokens as they arrive.
        """
        system_message = f"""You are a helpful HR assistant for Habuild, an internal company knowledge base.

Your role is to answer employee questions about HR policies based on the documents provided.

Guidelines:
1. Only answer based on the provided policy documents below.
2. If the answer is not in the documents, clearly state: "I don't have information about this in our current policies. Please contact HR."
3. Always cite which policy document you're referencing.
4. Be concise and professional.
5. If a question is outside HR policies (e.g., technical questions), politely redirect to appropriate departments.

{context}"""

        messages = conversation_history + [
            {"role": "user", "content": question}
        ]

        with self.client.messages.stream(
            model="claude-sonnet-4-5",
            max_tokens=2048,
            system=system_message,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                yield text

    def get_summary(self, text: str, max_tokens: int = 200) -> str:
        """Get a summary of text (used for document processing)."""
        response = self.client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=max_tokens,
            messages=[
                {
                    "role": "user",
                    "content": f"Summarize this text concisely:\n\n{text}"
                }
            ],
        )
        return response.content[0].text


llm_service = LLMService()
