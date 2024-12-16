"""
Basic usage examples for aigrok.

This module demonstrates common usage patterns for the aigrok library.
"""
from pathlib import Path
from aigrok import process_document, Config
from aigrok.types import ProcessingResult

def basic_text_extraction():
    """Basic text extraction from a PDF."""
    result = process_document(
        "sample.pdf",
        prompt="Extract the main content",
        model="gpt-3.5-turbo"
    )
    
    if result.success:
        print(f"Content: {result.text}")
        print(f"Page count: {result.page_count}")
    else:
        print(f"Error: {result.error}")

def structured_data_extraction():
    """Extract structured data in JSON format."""
    schema = {
        "title": "string",
        "authors": ["string"],
        "publication_date": "string",
        "abstract": "string"
    }
    
    result = process_document(
        "paper.pdf",
        prompt="Extract paper metadata",
        format="json",
        schema=schema
    )
    
    if result.success:
        metadata = result.metadata
        print(f"Title: {metadata['title']}")
        print(f"Authors: {', '.join(metadata['authors'])}")

def vision_analysis():
    """Analyze images in a PDF."""
    result = process_document(
        "presentation.pdf",
        prompt="Describe the charts and images",
        model="gpt-4-vision"
    )
    
    if result.success:
        print(f"Analysis: {result.text}")

def custom_configuration():
    """Example with custom configuration."""
    # Load config
    config = Config.load()
    
    # Update settings
    config.update(
        text_model="claude-3",
        vision_model="gemini-pro-vision",
        ocr_enabled=True,
        ocr_languages=["en", "es"]
    )
    
    # Save changes
    config.save()
    
    # Process with new config
    result = process_document("multilingual.pdf")
    print(f"Processed with {config.text_model}")

if __name__ == "__main__":
    basic_text_extraction()
    structured_data_extraction()
    vision_analysis()
    custom_configuration()
