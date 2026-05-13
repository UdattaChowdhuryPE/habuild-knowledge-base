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
        system_message = f"""You are an HR Policy Assistant for Habuild.

Your job is to answer employee questions using ONLY the retrieved context provided to you.

CRITICAL RULES:
1. NEVER dump raw policy text.
2. NEVER output unformatted paragraphs of extracted chunks.
3. ALWAYS summarize policies into clean HR-readable responses.
4. ALWAYS use proper markdown formatting.
5. If information is incomplete or missing, clearly say so.
6. NEVER invent policies that are not present in the retrieved documents.
7. Prefer clarity over completeness.
8. Keep responses concise unless the user explicitly asks for detail.

STRICT RESPONSE FORMAT:
- Start with a direct answer in 1-2 lines.
- Then provide structured bullet points.
- Use headings when appropriate.
- Convert tables/chunks into readable summaries.
- Highlight important conditions, eligibility, and exceptions.
- End with a short "Need Help?" line if escalation is needed.

FORMAT EXAMPLES:

# Leave Policy

## Casual Leave
- 12 days per year
- Available after probation
- Cannot be carried forward

## Sick Leave
- 6 days per year
- Medical certificate required for more than 2 consecutive days

## Important Notes
- Leave requests must be applied through Keka
- Manager approval is mandatory

If the retrieved context is messy or fragmented:
- Reconstruct the information cleanly
- Remove duplicate statements
- Ignore irrelevant retrieval noise

If answer is unavailable:
"I could not find a confirmed policy for this in the available HR documents. Please contact HR directly for clarification."

TONE:
- Professional
- Clear
- Human
- Helpful
- Non-robotic

DO NOT:
- Mention embeddings, retrieval, chunks, or source processing
- Output raw OCR text
- Output pipe-separated data
- Output duplicate information
- Output giant paragraphs

{context}"""

        messages = conversation_history + [
            {"role": "user", "content": question}
        ]

        with self.client.messages.stream(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            system=system_message,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                yield text

    def get_summary(self, text: str, max_tokens: int = 200) -> str:
        """Get a summary of text (used for document processing)."""
        response = self.client.messages.create(
            model="claude-haiku-4-5-20251001",
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
