"""
Advanced usage examples for aigrok.

This module demonstrates advanced features and patterns.
"""

import asyncio
from typing import List, Dict
from aigrok import process_document, process_documents
from aigrok.types import ProcessingResult


async def batch_processing(files: List[str], prompt: str) -> Dict[str, ProcessingResult]:
    """Process multiple documents concurrently.

    Args:
        files: List of file paths
        prompt: Processing prompt

    Returns:
        Dictionary mapping file paths to results
    """
    return await process_documents(files, prompt=prompt, max_concurrent=5)


async def streaming_processing(file_path: str) -> None:
    """Process a document with streaming output."""
    async for chunk in process_document(file_path, prompt="Analyze the content", stream=True):
        print(f"Chunk: {chunk.text}")


def custom_error_handling():
    """Example with custom error handling."""
    try:
        process_document("large_file.pdf", prompt="Extract key points", timeout=60, retries=3)
    except ValueError as e:
        print(f"Invalid parameters: {e}")
    except TimeoutError:
        print("Processing timed out")
    except Exception as e:
        print(f"Unexpected error: {e}")


def provider_specific_options():
    """Example using provider-specific options."""
    # OpenAI specific
    process_document("document.pdf", model="gpt-4", temperature=0.7, max_tokens=2000)

    # Anthropic specific
    process_document("document.pdf", model="claude-3", max_tokens_to_sample=2000, temperature=0.8)

    # Gemini specific
    process_document("document.pdf", model="gemini-pro", candidate_count=3, top_k=40)


def custom_output_formatting():
    """Example with custom output formatting."""
    # CSV output
    process_document("data.pdf", format="csv", columns=["title", "date", "author", "content"])

    # Markdown output
    process_document("report.pdf", format="markdown", headers=["Summary", "Key Points", "Conclusion"])

    # Custom JSON schema
    process_document(
        "paper.pdf",
        format="json",
        schema={
            "title": {"type": "string", "required": True},
            "authors": {"type": "array", "items": {"type": "string"}, "required": True},
            "citations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "page": {"type": "integer"},
                    },
                },
            },
        },
    )


async def main():
    """Run all examples."""
    # Batch processing
    files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
    await batch_processing(files, "Summarize the content")

    # Streaming
    await streaming_processing("large_doc.pdf")

    # Other examples
    custom_error_handling()
    provider_specific_options()
    custom_output_formatting()


if __name__ == "__main__":
    asyncio.run(main())
