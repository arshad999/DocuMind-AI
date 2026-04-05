from typing import List

SYSTEM_PROMPT = """
You are a professional document drafting assistant for enterprise teams.
Your task is to produce well-organized, legally and commercially accurate business documents.
When drafting, maintain the company tone, preserve structure, and keep the output professional and readable.
Use retrieved company content as context and avoid inventing unsupported facts.
"""

USER_PROMPT_TEMPLATE = """
Context:
{context}

User request:
{request}

Optional inputs:
{optional_inputs}

Produce the response as a structured document with clear headings, paragraphs, and list items where appropriate. Label each section.
If the request asks for a contract or corporate document, include an executive summary, scope, obligations, key terms, and next steps.
Only use the information from the retrieved context when it is directly relevant.
"""

def build_generation_prompt(context_chunks: List[str], request: str, optional_fields: dict[str, str]) -> List[dict[str, str]]:
    context_text = "\n\n---\n\n".join(context_chunks) if context_chunks else "No relevant document context was found."
    optional_inputs = "\n".join([f"{key}: {value}" for key, value in optional_fields.items() if value]) or "None"

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": USER_PROMPT_TEMPLATE.format(
                context=context_text,
                request=request,
                optional_inputs=optional_inputs,
            ),
        },
    ]
