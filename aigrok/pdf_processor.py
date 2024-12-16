"""PDF processing module for aigrok."""
import os
import base64
from io import BytesIO
from pathlib import Path
from typing import Optional, Dict, Any, Union, List, Tuple
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
from .formats import validate_format
from .validation import validate_request
from .types import ProcessingResult
from .logging import configure_logging

class PDFProcessingResult(ProcessingResult):
    """Extended result for PDF processing."""
    vision_response: Optional[Any] = None
    ocr_text: Optional[str] = None
    ocr_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)

class PDFProcessor:
    """Processor for PDF documents."""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """Initialize PDF processor with optional configuration."""
        configure_logging()
        logger.debug("Initializing PDF processor")
        self.config_manager = config_manager or ConfigManager()
        
        if not self.config_manager.config:
            raise RuntimeError("PDF processor not properly initialized. Please run with --configure first.")
        
        # Initialize OCR if enabled
        if self.config_manager.config.ocr_enabled:
            logger.info(f"Initializing EasyOCR with languages: {self.config_manager.config.ocr_languages}")
            try:
                self.reader = easyocr.Reader(self.config_manager.config.ocr_languages)
            except Exception as e:
                if self.config_manager.config.ocr_fallback:
                    logger.warning(f"Failed to initialize OCR: {e}. Continuing without OCR due to fallback setting.")
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
                if text_model.provider == 'ollama':
                    self.llm = ollama.Client(
                        host=text_model.endpoint,
                        timeout=httpx.Timeout(30.0, connect=10.0)  # 30s total timeout, 10s connect timeout
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
                if vision_model.provider == 'ollama':
                    if not hasattr(self, 'llm'):
                        self.llm = ollama.Client(
                            host=vision_model.endpoint,
                            timeout=httpx.Timeout(60.0, connect=10.0)  # 60s total timeout, 10s connect timeout
                        )
                elif vision_model.provider not in ['ollama']:
                    # TODO(#128): Add support for other vision providers
                    logger.warning(f"Vision provider {vision_model.provider} not yet supported")
                    
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
                    logger.warning(f"Failed to process image {img_index} on page {page_num}: {e}")
                    continue
        
        return images
    
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
        """Combine PDF text with OCR text.
        
        Args:
            pdf_text: Text extracted directly from PDF
            ocr_text: Text extracted via OCR
            
        Returns:
            Combined text with clear separation between sources
            
        Note:
            OCR text is clearly marked in the output to distinguish it from
            directly extracted PDF text.
        """
        result = []
        if pdf_text and pdf_text.strip():
            result.append("Text extracted from PDF:")
            result.append(pdf_text.strip())
            
        if ocr_text and ocr_text.strip():
            if result:
                result.append("\n")
            result.append("Text extracted via OCR:")
            result.append(ocr_text.strip())
            
        return "\n".join(result) if result else ""
    
    def process_file(self, file_path: Union[str, Path], prompt: str = None, **kwargs) -> PDFProcessingResult:
        """Process a PDF file."""
        if not self._initialized:
            return PDFProcessingResult(
                success=False,
                error="PDF processor not properly initialized. Please run with --configure first."
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
                'format': 'PDF',
                'page_count': len(doc),
                'file_size': os.path.getsize(file_path),
                'file_name': os.path.basename(file_path)
            }
            
            # Add PDF metadata if available
            if doc.metadata:
                metadata.update({
                    'title': doc.metadata.get('title', ''),
                    'author': doc.metadata.get('author', ''),
                    'subject': doc.metadata.get('subject', ''),
                    'keywords': doc.metadata.get('keywords', ''),
                    'creator': doc.metadata.get('creator', ''),
                    'producer': doc.metadata.get('producer', ''),
                    'creation_date': doc.metadata.get('creationDate', ''),
                    'modification_date': doc.metadata.get('modDate', '')
                })
            logger.debug(f"Extracted metadata: {metadata}")
            
            # Extract text and images
            text_content = []
            images = []
            total_chars = 0
            total_images = 0
            
            for page_num, page in enumerate(doc, 1):
                # Extract text
                page_text = page.get_text()
                if page_text.strip():
                    text_content.append(page_text)
                total_chars += len(page_text)
                logger.debug(f"Page {page_num} extracted {len(page_text)} chars")
                
                # Extract images
                page_images = self._extract_images(doc)
                if page_images:
                    images.extend(page_images)
                    total_images += len(page_images)
                logger.debug(f"Page {page_num} extracted {len(page_images)} images")
            
            # Determine content type
            content_type = 'mixed'
            if total_chars == 0 and total_images > 0:
                content_type = 'images_only'
            elif total_chars > 0 and total_images == 0:
                content_type = 'text_only'
            logger.debug(f"PDF content type: {content_type}")
            
            # Combine extracted text
            combined_text = "\n\n".join(text_content)
            logger.debug(f"Extracted text: {combined_text[:100]}...")
            logger.debug(f"Extracted {total_images} total images")
            
            # Process with OCR if enabled
            ocr_text = ""
            ocr_confidence = 0.0
            if self.reader and images:
                logger.debug("Processing images with OCR")
                ocr_results = []
                for img, page_num in images:
                    text, conf = self._process_image_ocr(img)
                    if text:
                        ocr_results.append((text, conf, page_num))
                
                if ocr_results:
                    # Sort by page number
                    ocr_results.sort(key=lambda x: x[2])
                    
                    # Combine results
                    ocr_texts = []
                    total_conf = 0.0
                    for text, conf, page in ocr_results:
                        ocr_texts.append(f"[Page {page}]\n{text}")
                        total_conf += conf
                    
                    ocr_text = "\n\n".join(ocr_texts)
                    ocr_confidence = total_conf / len(ocr_results)
                    logger.debug(f"OCR confidence: {ocr_confidence:.2%}")
            
            # If we have OCR results, use text model instead of vision
            if ocr_text and ocr_confidence and ocr_confidence > 0.8:
                logger.debug("Using text model with OCR results")
                combined_text = self._combine_text("", ocr_text)  # Only use OCR text since PDF text is empty
                llm_response = self._query_llm(
                    prompt=prompt,
                    context=combined_text,
                    provider=self.text_provider
                )
            elif content_type == 'images_only' and self.vision_provider:
                logger.debug("Sending to vision LLM for analysis")
                llm_response = self._query_llm(
                    prompt=prompt,
                    context=combined_text,
                    provider=self.vision_provider,
                    images=[(img, f"Page {page}") for img, page in images]
                )
            else:
                logger.debug("Sending to text LLM for analysis")
                llm_response = self._query_llm(
                    prompt=prompt,
                    context=self._combine_text(combined_text, ocr_text),
                    provider=self.text_provider
                )
            logger.debug(f"LLM response: {llm_response[:100]}...")
            
            return PDFProcessingResult(
                success=True,
                text=combined_text,
                metadata=metadata,
                page_count=len(doc),
                ocr_text=ocr_text,
                ocr_confidence=ocr_confidence,
                llm_response=llm_response
            )
            
        except Exception as e:
            logger.error(f"Failed to process file: {e}")
            return PDFProcessingResult(
                success=False,
                error=str(e)
            )

    def _query_llm(self, prompt: str, context: str, provider: str, images: Optional[List[Tuple[Image.Image, str]]] = None):
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
                if provider == 'ollama':
                    try:
                        response = self.llm.generate(
                            model=self.text_model,
                            prompt=f"""Based on the following document:

Context:
{context}

Question: {prompt}

Please answer the question using only information from the document above.""",
                            stream=False
                        )
                        return response['response'] if isinstance(response, dict) else response.response
                    except httpx.TimeoutException:
                        logger.error("Request timed out")
                        return "Error: Request timed out. Please try again."
                    except Exception as e:
                        logger.error(f"Error querying text LLM: {e}")
                        return f"Error querying LLM: {e}"
                else:
                    response = self.llm.completion(
                        model=f"{self.text_provider}/{self.text_model}",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant analyzing documents."},
                            {"role": "user", "content": f"Document content:\n\n{context}\n\nPrompt: {prompt}"}
                        ]
                    )
                    return response.choices[0].message.content
                    
            else:
                # Vision query
                if provider == 'ollama':
                    try:
                        # Convert images to base64
                        image_data = []
                        for img, desc in images:
                            # Convert PIL Image to bytes
                            img_byte_arr = BytesIO()
                            img.save(img_byte_arr, format='PNG')  # Try PNG format
                            img_byte_arr = img_byte_arr.getvalue()
                            
                            # Convert to base64
                            img_b64 = base64.b64encode(img_byte_arr).decode('utf-8')
                            image_data.append(img_b64)
                        
                        # Since OCR already worked, let's use the text for context
                        context = context if context else ""
                        
                        response = self.llm.generate(
                            model=self.vision_model,
                            prompt=f"Here is the OCR text for context:\n{context}\n\nPlease analyze the image and answer: {prompt}",
                            images=image_data,
                            stream=False
                        )
                        return response['response'] if isinstance(response, dict) else response.response
                    except httpx.TimeoutException:
                        logger.error("Vision request timed out")
                        return "Error: Vision request timed out. Please try again."
                    except Exception as e:
                        logger.error(f"Error querying vision LLM: {e}")
                        return f"Error querying LLM: {e}"
                else:
                    raise ValueError(f"Vision queries not supported for provider {provider}")
                    
        except Exception as e:
            logger.error(f"LLM query failed: {e}")
            return f"Error querying LLM: {e}..."
            
    def process_document(self, file_path: Union[str, Path], prompt: str,
                      format: str = 'text', **kwargs) -> PDFProcessingResult:
        """Process a document with the configured model."""
        if not self._initialized:
            return PDFProcessingResult(
                success=False,
                error="Processor not initialized. Please configure first."
            )

        try:
            # Validate format
            format = validate_format(format)
            
            # Load and process the PDF
            doc = fitz.open(file_path)
            pdf_text = ""
            for page in doc:
                page_text = page.get_text()
                if page_text.strip():
                    pdf_text += page_text + "\n"
                
            # Process images with OCR if enabled
            ocr_text = ""
            ocr_confidence = 0.0
            
            if self.reader:
                images = self._extract_images(doc)
                ocr_results = []
                confidences = []
                
                for image, page_num in images:
                    text, conf = self._process_image_ocr(image)
                    if text:
                        ocr_results.append(f"[Page {page_num + 1}] {text}")
                        confidences.append(conf)
                
                if ocr_results:
                    ocr_text = "\n".join(ocr_results)
                    ocr_confidence = sum(confidences) / len(confidences)
            
            # Combine texts
            combined_text = self._combine_text(pdf_text.strip(), ocr_text)
            
            # Process with LLM
            if self.text_provider == "ollama":
                try:
                    response = self.llm.generate(
                        model=self.text_model,
                        prompt=f"Context:\n{combined_text}\n\nPrompt: {prompt}",
                        stream=False
                    )
                    llm_response = response.response
                except httpx.TimeoutException:
                    logger.error("Request timed out")
                    return PDFProcessingResult(
                        success=False,
                        error="Error: Request timed out. Please try again."
                    )
                except Exception as e:
                    logger.error(f"Error processing document: {e}")
                    return PDFProcessingResult(
                        success=False,
                        error=str(e)
                    )
            else:
                messages = [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant processing document content."
                    },
                    {
                        "role": "user",
                        "content": f"Document content:\n\n{combined_text}\n\nPrompt: {prompt}"
                    }
                ]
                response = self.llm.completion(
                    model=f"{self.text_provider}/{self.text_model}",
                    messages=messages
                )
                llm_response = response.choices[0].message.content
            
            return PDFProcessingResult(
                success=True,
                text=combined_text,
                metadata={"filename": os.path.basename(file_path)},
                page_count=len(doc),
                llm_response=llm_response,
                ocr_text=ocr_text if ocr_text else None,
                ocr_confidence=ocr_confidence if ocr_confidence > 0 else None
            )
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return PDFProcessingResult(
                success=False,
                error=str(e)
            )