import os
from anthropic import Anthropic
from typing import List, Dict, Any, Generator
from backend.services.tools import TOOLS, execute_tool


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
        conversation_history: List[Dict[str, str]],
        user_location: str
    ) -> Generator[str, None, None]:
        """
        Stream a response from Claude using conversation history and retrieved context.
        Supports tool use for employee queries. Yields tokens as they arrive.
        """
        system_message = f"""You are an HR Policy Assistant for Habuild.

Employee location: {user_location}

Your job is to answer employee questions using the available tools and retrieved context.

CRITICAL RULES:
1. For HR policy questions, use retrieved context.
2. For ANY employee information (email address, location, role, headcount, name lookup, contact details), ALWAYS use the provided tools. Never guess or invent employee data.
3. NEVER dump raw policy text.
4. NEVER output unformatted paragraphs of extracted chunks.
5. ALWAYS summarize policies into clean HR-readable responses.
6. ALWAYS use proper markdown formatting.
7. If information is incomplete or missing, clearly say so.
8. NEVER invent policies that are not present in the retrieved documents.
9. Prefer clarity over completeness.
10. Keep responses concise unless the user explicitly asks for detail.

EMPLOYEE LOOKUP RESPONSE FORMAT:
When a user asks for an employee's email or contact details, you MUST:
- State their full name clearly
- State their email address explicitly (NEVER omit the email when it is available from the tool result)
- Include location if relevant
Do not just list raw employee objects. Format the response as a clean summary:
Example: **Saurabh Bothra** — saurabh.bothra@habuild.in (Gurugram)

LOCATION RULE (HIGHEST PRIORITY for policy questions):
If the user asks about HR policies, leave, benefits, or any information that pertains to a location OTHER than {user_location}, do NOT provide that information.
Instead respond exactly:
"I can only provide HR information relevant to your location ({user_location}). For policies at other locations, please reach out to HR directly."

STRICT RESPONSE FORMAT (when answering allowed location questions):
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

        # Phase 1: Stream with tools enabled
        # Tokens arrive in real-time, stop_reason tells us if tool was used
        with self.client.messages.stream(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            system=system_message,
            tools=TOOLS,
            messages=messages,
        ) as stream:
            # Yield text tokens as they arrive (sync generator, runs in thread pool)
            yield from stream.text_stream
            
            # Get final message to check if a tool was used
            final_message = stream.get_final_message()
        
        # Check if Claude wants to use a tool
        if final_message.stop_reason == "tool_use":
            # Collect ALL tool results (Anthropic API requires all tool_use blocks paired with tool_results)
            tool_results = []
            for content_block in final_message.content:
                if content_block.type == "tool_use":
                    try:
                        tool_result = execute_tool(content_block.name, content_block.input)
                    except Exception as e:
                        tool_result = f"Error executing {content_block.name}: {str(e)}"
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": content_block.id,
                        "content": tool_result,
                    })
            
            if tool_results:
                # Add the assistant response and all tool results to messages
                messages.append({"role": "assistant", "content": final_message.content})
                messages.append({"role": "user", "content": tool_results})
                
                # Phase 2: Stream final response after tool execution
                with self.client.messages.stream(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=2048,
                    system=system_message,
                    tools=TOOLS,
                    messages=messages,
                ) as stream2:
                    yield from stream2.text_stream

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
