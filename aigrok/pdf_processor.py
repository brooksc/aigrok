"""PDF processing module for aigrok."""

import os
import base64
from io import BytesIO
from pathlib import Path
from typing import Optional, Any, Union, List, Tuple
from pydantic import Field
from loguru import logger
import fitz  # PyMuPDF
from PIL import Image
import ollama
import litellm
import easyocr
import numpy as np
import httpx
from .config import ConfigManager
from .types import ProcessingResult
from pprint import pformat

# Constants
CONNECT_TIMEOUT_SECONDS = 10.0  # Connection timeout
TOTAL_TIMEOUT_SECONDS = 90.0  # Total operation timeout


class PDFProcessingResult(ProcessingResult):
    """Extended result for PDF processing."""

    vision_response: Optional[Any] = None
    ocr_text: Optional[str] = None
    ocr_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class PDFProcessor:
    """Processor for PDF documents."""

    def __init__(
        self, config_manager: Optional[ConfigManager] = None, verbose: bool = False
    ):
        """Initialize PDF processor with optional configuration."""
        self.verbose = verbose
        logger.debug("Initializing PDF processor")
        self.config_manager = config_manager or ConfigManager()

        if not self.config_manager.config:
            raise RuntimeError(
                "PDF processor not properly initialized. Please run with --configure first."
            )

        # Initialize OCR if enabled
        if self.config_manager.config.ocr_enabled:
            if self.verbose:
                logger.info(
                    f"Initializing EasyOCR with languages: {self.config_manager.config.ocr_languages}"
                )
            try:
                self.reader = easyocr.Reader(self.config_manager.config.ocr_languages)
            except Exception as e:
                if self.config_manager.config.ocr_fallback:
                    if self.verbose:
                        logger.warning(
                            f"Failed to initialize OCR: {e}. Continuing without OCR due to fallback setting."
                        )
                    self.reader = None
                else:
                    raise RuntimeError(f"Failed to initialize OCR: {e}")
        else:
            self.reader = None

        # Initialize models
        try:
            # Initialize text model
            self.text_provider = None
            self.text_model = None
            if self.config_manager.config.text_model:
                text_model = self.config_manager.config.text_model
                self.text_provider = text_model.provider
                self.text_model = text_model.model_name
                if text_model.provider == "ollama":
                    self.llm = ollama.Client(
                        host=text_model.endpoint,
                        timeout=httpx.Timeout(
                            TOTAL_TIMEOUT_SECONDS, connect=CONNECT_TIMEOUT_SECONDS
                        ),  # 30s total timeout, 10s connect timeout
                    )
                else:
                    litellm.set_verbose = True
                    self.llm = litellm

            # Initialize vision model
            self.vision_provider = None
            self.vision_model = None
            self.vision_endpoint = None
            if self.config_manager.config.vision_model:
                vision_model = self.config_manager.config.vision_model
                self.vision_provider = vision_model.provider
                self.vision_model = vision_model.model_name
                self.vision_endpoint = vision_model.endpoint
                if vision_model.provider == "ollama":
                    if not hasattr(self, "llm"):
                        self.llm = ollama.Client(
                            host=vision_model.endpoint,
                            timeout=httpx.Timeout(
                                TOTAL_TIMEOUT_SECONDS, connect=CONNECT_TIMEOUT_SECONDS
                            ),  # 300s total timeout, 10s connect timeout
                        )
                elif vision_model.provider == "openai":
                    if not hasattr(self, "llm"):
                        self.llm = litellm
                else:
                    # Other providers not yet supported
                    logger.warning(
                        f"Vision provider {vision_model.provider} not yet supported"
                    )

            self._initialized = True

        except Exception as e:
            logger.error(f"Failed to initialize models: {e}")
            self.text_provider = None
            self.text_model = None
            self.vision_provider = None
            self.vision_model = None
            self.vision_endpoint = None
            self._initialized = False
            raise RuntimeError(f"Failed to initialize models: {e}")

        # Log configuration in verbose mode
        logger.debug(
            "PDF Processor Configuration:\n%s",
            pformat(
                {
                    "ocr_enabled": self.config_manager.config.ocr_enabled,
                    "ocr_languages": self.config_manager.config.ocr_languages,
                    "ocr_fallback": self.config_manager.config.ocr_fallback,
                    "config": self.config_manager.config.model_dump()
                    if self.config_manager
                    else None,
                }
            ),
        )

    def _extract_images(self, doc: fitz.Document) -> List[Tuple[Image.Image, int]]:
        """Extract images from PDF document.

        Args:
            doc: PyMuPDF document object

        Returns:
            List of tuples containing (PIL Image, page number)

        Note:
            Images are extracted in their original format and converted to PIL Images
            for OCR processing. Page numbers are zero-based.
        """
        images = []
        for page_num, page in enumerate(doc):
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                xref = img[0]
                try:
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image = Image.open(BytesIO(image_bytes))
                    images.append((image, page_num))
                except Exception as e:
                    logger.warning(
                        f"Failed to process image {img_index} on page {page_num}: {e}"
                    )
                    continue

        return images

    def _process_ocr_results(
        self, results: List[Tuple[List[List[int]], str, float]], page_num: int
    ) -> Tuple[str, float]:
        """Process OCR results for a page."""
        if not results:
            return "", 0.0

        texts = []
        confidences = []
        for _, text, conf in results:
            texts.append(text)
            confidences.append(conf)

        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        combined_text = f"[Page {page_num + 1}] {' '.join(texts)}"
        return combined_text, avg_confidence

    def _process_image_ocr(self, image: Image.Image) -> Tuple[str, float]:
        """Process image with EasyOCR.

        Args:
            image: PIL Image object to process

        Returns:
            Tuple of (extracted text, confidence score)

        Note:
            Confidence score is averaged across all detected text regions.
            Returns empty string and 0.0 confidence if OCR fails or is not configured.
        """
        if not self.reader:
            return "", 0.0

        # Convert PIL Image to numpy array
        img_array = np.array(image)

        try:
            results = self.reader.readtext(img_array)

            # Combine all text with their confidence scores
            texts = []
            total_confidence = 0.0

            for bbox, text, confidence in results:
                texts.append(text)
                total_confidence += confidence

            combined_text = " ".join(texts)
            avg_confidence = total_confidence / len(results) if results else 0.0

            return combined_text, avg_confidence

        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            return "", 0.0

    def _combine_text(self, pdf_text: str, ocr_text: str) -> str:
        """Combine extracted PDF text with OCR text."""
        combined = []

        if pdf_text:
            combined.append("Text extracted from PDF:")
            combined.append(pdf_text.strip())

        if ocr_text:
            if combined:
                combined.append("\nText extracted via OCR:")
            else:
                combined.append("Text extracted via OCR:")
            combined.append(ocr_text.strip())

        return "\n".join(combined)

    def _query_llm(
        self,
        prompt: str,
        context: str,
        provider: str,
        images: Optional[List[Tuple[Image.Image, str]]] = None,
    ):
        """Query the LLM with prompt and context.

        Args:
            prompt: User prompt
            context: Text context
            provider: Provider to use
            images: Optional list of tuples containing (image, description)
        """
        try:
            logger.debug(f"Processing {len(images) if images else 0} images")

            if not images:
                # Text-only query
                response = None
                if provider == "ollama":
                    try:
                        response = self.llm.chat(
                            model=self.text_model,
                            messages=[
                                {
                                    "role": "user",
                                    "content": f"""Based on the following document:

Context:
{context}

Question: {prompt}

Please answer the question using only information from the document above.""",
                                }
                            ],
                        )
                        logger.debug(
                            "LLM Request:\n%s",
                            pformat(
                                {
                                    "model": self.text_model,
                                    "provider": provider,
                                    "prompt": prompt,
                                    "text_length": len(context) if context else 0,
                                }
                            ),
                        )
                        logger.debug(
                            "LLM Response:\n%s",
                            pformat({"response": response.message.content}),
                        )
                        return response.message.content
                    except httpx.TimeoutException:
                        logger.error("Request timed out")
                        return "Error: Request timed out. Please try again."
                    except Exception as e:
                        logger.error(f"Error querying text LLM: {e}")
                        return f"Error querying LLM: {e}"
                else:
                    messages = [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant processing document content.",
                        },
                        {
                            "role": "user",
                            "content": f"Document content:\n\n{context}\n\nPrompt: {prompt}",
                        },
                    ]
                    response = litellm.completion(
                        model=f"{self.text_provider}/{self.text_model}",
                        messages=messages,
                    )
                    logger.debug(
                        "LLM Request:\n%s",
                        pformat(
                            {
                                "model": self.text_model,
                                "provider": provider,
                                "prompt": prompt,
                                "text_length": len(context) if context else 0,
                            }
                        ),
                    )
                    logger.debug(
                        "LLM Response:\n%s",
                        pformat(
                            {
                                "response": response.choices[0].message.content
                                if hasattr(response, "choices")
                                else response
                            }
                        ),
                    )

                    # Handle both dictionary and object responses
                    if hasattr(response, "choices") and response.choices:
                        return response.choices[0].message.content
                    elif (
                        isinstance(response, dict)
                        and "choices" in response
                        and response["choices"]
                    ):
                        return response["choices"][0]["message"]["content"]
                    else:
                        logger.error(f"Unexpected response format: {response}")
                        return None
            else:
                # Vision query
                if not images:
                    return "No images found to analyze"

                # Prepare images for vision model
                base64_images = []
                for img, _ in images:
                    # Convert to base64
                    buffered = BytesIO()
                    img.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    base64_images.append(img_str)

                # Query vision model
                if provider == "ollama":
                    # Prepare prompt with images
                    prompt_text = f"""Please analyze these document images and answer the following question:

Question: {prompt}

Please be concise and only include information that directly answers the question."""

                    # Add images to prompt
                    for img_str in base64_images:
                        prompt_text += (
                            f"\n<image>data:image/png;base64,{img_str}</image>"
                        )

                    try:
                        response = self.llm.chat(
                            model=self.vision_model,
                            messages=[{"role": "user", "content": prompt_text}],
                        )

                        logger.debug(
                            "LLM Request:\n%s",
                            pformat(
                                {
                                    "model": self.vision_model,
                                    "provider": provider,
                                    "prompt": prompt,
                                    "text_length": len(prompt_text)
                                    if prompt_text
                                    else 0,
                                }
                            ),
                        )
                        logger.debug(
                            "LLM Response:\n%s",
                            pformat({"response": response.message.content}),
                        )

                        logger.debug(f"Raw LLM Response: {response}")

                        if response and hasattr(response, "message"):
                            return response.message.content
                        else:
                            raise ValueError("Unexpected response format from LLM")

                    except Exception as e:
                        logger.error(f"Error querying Ollama vision: {e}")
                        return f"Error querying vision LLM: {e}"
                elif provider == "openai":
                    # OpenAI vision handling (existing code)
                    messages = [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant analyzing documents.",
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"Please analyze these document images and answer the following question: {prompt}",
                                }
                            ],
                        },
                    ]

                    # Add images to messages
                    for img_str in base64_images:
                        messages[1]["content"].append(
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_str}"
                                },
                            }
                        )

                    try:
                        response = litellm.completion(
                            model=f"{self.vision_provider}/{self.vision_model}",
                            messages=messages,
                            max_tokens=1000,
                        )

                        logger.debug(
                            "LLM Request:\n%s",
                            pformat(
                                {
                                    "model": f"{self.vision_provider}/{self.vision_model}",
                                    "provider": provider,
                                    "prompt": prompt,
                                    "messages": messages,
                                }
                            ),
                        )
                        logger.debug(
                            "LLM Response:\n%s",
                            pformat(
                                {
                                    "response": response.choices[0].message.content
                                    if hasattr(response, "choices")
                                    else response
                                }
                            ),
                        )

                        # Handle both dictionary and object responses
                        if hasattr(response, "choices") and response.choices:
                            return response.choices[0].message.content
                        elif (
                            isinstance(response, dict)
                            and "choices" in response
                            and response["choices"]
                        ):
                            return response["choices"][0]["message"]["content"]
                        else:
                            logger.error(f"Unexpected response format: {response}")
                            return None
                    except Exception as e:
                        logger.error(f"Error querying OpenAI vision: {e}")
                        return f"Error querying vision LLM: {e}"
                else:
                    raise ValueError(f"Unsupported vision provider: {provider}")

        except Exception as e:
            error_msg = f"Error querying LLM: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def process_file(
        self, file_path: Union[str, Path], prompt: str = None, **kwargs
    ) -> PDFProcessingResult:
        """Process a PDF file."""
        if not self._initialized:
            return PDFProcessingResult(
                success=False,
                error="PDF processor not properly initialized. Please run with --configure first.",
            )

        try:
            logger.debug(f"Processing file: {file_path}")
            logger.debug(f"Prompt: {prompt}")
            logger.debug(f"Additional args: {kwargs}")

            # Validate request
            logger.debug("Validating request")
            if not os.path.exists(file_path):
                raise ValueError(f"File not found: {file_path}")
            logger.debug(f"Validated file path: {file_path}")

            # Open PDF
            doc = fitz.open(file_path)
            logger.debug(f"PDF has {len(doc)} pages")

            # Extract metadata
            metadata = {
                "format": "PDF",
                "page_count": len(doc),
                "file_size": os.path.getsize(file_path),
                "file_name": os.path.basename(file_path),
            }

            # Add PDF metadata if available
            if doc.metadata:
                metadata.update(
                    {
                        "title": doc.metadata.get("title", ""),
                        "author": doc.metadata.get("author", ""),
                        "subject": doc.metadata.get("subject", ""),
                        "keywords": doc.metadata.get("keywords", ""),
                        "creator": doc.metadata.get("creator", ""),
                        "producer": doc.metadata.get("producer", ""),
                        "creation_date": doc.metadata.get("creationDate", ""),
                        "modification_date": doc.metadata.get("modDate", ""),
                    }
                )
            logger.debug(f"Extracted metadata: {metadata}")

            # Extract text and images
            extracted_text = []
            images = []
            for page_num, page in enumerate(doc):
                # Extract text
                page_text = page.get_text()
                if page_text.strip():
                    extracted_text.append(page_text)

                # Extract images
                page_images = self._extract_images(doc)
                if page_images:
                    images.extend(page_images)

            # Determine content type
            content_type = "text_only"
            if len(extracted_text) == 0 and len(images) > 0:
                content_type = "images_only"
                logger.debug(f"PDF content type: {content_type}")
            elif len(images) > 0:
                content_type = "mixed"
                logger.debug(f"PDF content type: {content_type}")

            logger.debug(f"Extracted text: {extracted_text}")
            logger.debug(f"Extracted {len(images)} total images")

            # Process with OCR if needed
            ocr_text = []
            ocr_confidence = 0.0
            if content_type in ["images_only", "mixed"] and self.reader:
                logger.debug("Processing images with OCR")
                total_confidence = 0
                total_regions = 0

                for img, _ in images:
                    text, confidence = self._process_image_ocr(img)
                    if text:
                        ocr_text.append(text)
                        total_confidence += confidence
                        total_regions += 1

                if total_regions > 0:
                    ocr_confidence = total_confidence / total_regions
                    logger.debug(f"OCR confidence: {ocr_confidence:.2%}")

            # Use vision model for image-only PDFs, otherwise use text model
            if content_type == "images_only" and self.vision_model:
                logger.debug("Using vision model for image analysis")
                result = self._query_llm(prompt, "", self.vision_provider, images)
            else:
                logger.debug(
                    f"Using text model with OCR results (confidence: {ocr_confidence:.2%})"
                )
                result = self._query_llm(
                    prompt,
                    self._combine_text(
                        "\n".join(extracted_text),
                        "\n".join(ocr_text) if ocr_text else None,
                    ),
                    self.text_provider,
                )

            if prompt:
                try:
                    return ProcessingResult(
                        success=True,
                        text=self._combine_text(
                            "\n".join(extracted_text),
                            "\n".join(ocr_text) if ocr_text else None,
                        ),
                        page_count=len(doc),
                        llm_response=result,
                        metadata=metadata,
                    )
                except Exception as e:
                    logger.error(f"Error querying LLM: {e}")
                    return ProcessingResult(
                        success=False,
                        text=None,
                        page_count=None,
                        llm_response=None,
                        error=f"Error querying LLM: {e}",
                        metadata=metadata,
                    )

            # Return text only if no prompt
            return ProcessingResult(
                success=True,
                text=self._combine_text(
                    "\n".join(extracted_text), "\n".join(ocr_text) if ocr_text else None
                ),
                page_count=len(doc),
                metadata=metadata,
            )

        except Exception as e:
            logger.error(f"Failed to process file: {e}")
            return ProcessingResult(success=False, error=str(e))

    def process_document(
        self, file_path: Union[str, Path], prompt: Optional[str] = None
    ) -> PDFProcessingResult:
        """Process a PDF document."""
        try:
            doc = fitz.open(file_path)
            text_content = []
            ocr_results = []
            ocr_confidences = []

            for page_num, page in enumerate(doc):
                # Extract text
                text_content.append(page.get_text())

                # Handle OCR if enabled
                if self.reader is not None:
                    images = self._extract_images(page)
                    for image, _ in images:
                        try:
                            results = self.reader.readtext(np.array(image))
                            if results:
                                ocr_text, ocr_conf = self._process_ocr_results(
                                    results, page_num
                                )
                                ocr_results.append(ocr_text)
                                ocr_confidences.append(ocr_conf)
                        except Exception as e:
                            if self.verbose:
                                logger.warning(f"OCR failed for an image: {e}")
                            if not self.config_manager.config.ocr_fallback:
                                raise

            # Combine text
            pdf_text = "\n".join(text_content)
            ocr_text = "\n".join(ocr_results) if ocr_results else None
            ocr_confidence = (
                sum(ocr_confidences) / len(ocr_confidences) if ocr_confidences else None
            )

            combined_text = (
                self._combine_text(pdf_text, ocr_text) if ocr_text else pdf_text
            )

            # Process with LLM if prompt provided
            llm_response = None
            if prompt and self.text_provider and self.text_model:
                if self.text_provider == "ollama":
                    response = self.llm.generate(
                        model=self.text_model,
                        prompt=f"{prompt}\n\nDocument content:\n{combined_text}",
                    )
                    logger.debug(
                        "LLM Request:\n%s",
                        pformat(
                            {
                                "model": self.text_model,
                                "provider": self.text_provider,
                                "prompt": prompt,
                                "text_length": len(combined_text)
                                if combined_text
                                else 0,
                            }
                        ),
                    )
                    logger.debug(
                        "LLM Response:\n%s", pformat({"response": response["response"]})
                    )
                    llm_response = response["response"]

            return PDFProcessingResult(
                success=True,
                text=combined_text,
                metadata=None,  # TODO: Add metadata extraction
                page_count=len(doc),
                error=None,
                llm_response=llm_response,
                filename=str(file_path),
                vision_response=None,
                ocr_text=ocr_text,
                ocr_confidence=ocr_confidence,
            )

        except Exception as e:
            error_msg = f"Failed to process document: {str(e)}"
            if self.verbose:
                logger.error(error_msg)
            return PDFProcessingResult(
                success=False,
                text=None,
                metadata=None,
                page_count=0,
                error=error_msg,
                llm_response=None,
                filename=str(file_path),
                vision_response=None,
                ocr_text=None,
                ocr_confidence=None,
            )
