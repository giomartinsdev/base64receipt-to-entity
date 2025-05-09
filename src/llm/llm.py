"""
Language Model Processing Module

This module provides functions for processing receipt text using language models
to extract structured information.
"""

from typing import Optional
import logging
import torch
import json
from transformers import Pipeline, pipeline
import os
from dotenv import load_dotenv
from huggingface_hub import login
from src.entities.receipt import Receipt
from src.llm.prompt import PROMPT
from src.utils.text import apply_regex

load_dotenv(override=True)

def login_huggingface(token: str) -> bool:
    """
    Login to Hugging Face with the provided token or from environment variable.
    
    This function authenticates with the Hugging Face Hub, allowing access to
    gated models and features that require authentication.
    
    Args:
        token str: Hugging Face API token. If None, will attempt to
                             get from HF_TOKEN environment variable.
    
    Returns:
        bool: True if login was successful, False otherwise

    """
    try:        
        login(token=token)
        logging.info("Successfully logged in to Hugging Face Hub")
        return True
    except Exception as e:
        logging.error(f"Failed to login to Hugging Face Hub: {str(e)}")
        return False


def get_pipeline() -> Pipeline:
    """
    Initialize and return a text generation pipeline with appropriate settings.
    
    The function detects available hardware and configures the pipeline accordingly,
    with optimized settings for either GPU or CPU usage.
    
    Returns:
        Pipeline: A configured text generation pipeline
    """
    login_huggingface(os.getenv("HF_TOKEN"))

    # Check if CUDA is available, otherwise fall back to CPU
    has_cuda = torch.cuda.is_available()
    
    if has_cuda:
        # Set memory efficient settings for CUDA
        torch.cuda.empty_cache()  # Clear CUDA cache before loading model
        
        # When using device_map="auto", don't specify device parameter
        return pipeline(
            "text-generation", 
            model=os.getenv("MODEL_NAME"),
            torch_dtype=torch.bfloat16,
            model_kwargs={
                "low_cpu_mem_usage": True,
                "device_map": os.getenv("DEVICE", "auto"),
            }
        )
    else:
        return pipeline(
            "text-generation", 
            model=os.getenv("MODEL_NAME"),
            device="cpu",
            model_kwargs={"low_cpu_mem_usage": True}
        )

def llm_parse_text_to_receipt(logger: logging.Logger, text: str) -> Optional[Receipt]:
    """
    Parse text extracted from a receipt image using a language model.
    
    This function processes the text through an LLM to extract structured information
    and returns it as a Receipt object. It includes automatic handling of text length,
    memory optimization, and fallback mechanisms for error cases.
    
    Args:
        logger (logging.Logger): Logger for recording processing information
        text (str): Text extracted from receipt image
        
    Returns:
        Optional[Receipt]: A Receipt object with structured data, or None if processing failed
    """
    try:
        # Get token count estimate (to prevent processing texts that are too long)
        original_length = len(text)
        max_length = 4000  # Reduced from 10000 to help with memory issues
        
        if original_length > max_length:
            logger.warning(f"Text too long ({original_length} chars), truncating to {max_length}...")
            # Keep the beginning and end of the text since receipts often have important information there
            beginning = text[:int(max_length * 0.7)]  # Keep 70% from the beginning
            end = text[-(int(max_length * 0.3)):]     # Keep 30% from the end
            text = beginning + end
        
        pipe = get_pipeline()
        formatted_prompt = PROMPT.format(text=text)
        
        # Use more memory-efficient generation settings
        result = pipe(
            formatted_prompt, 
            max_new_tokens=80,           # Reduced from 100
            do_sample=False,             # Deterministic generation uses less memory
            num_return_sequences=1,
            pad_token_id=pipe.tokenizer.eos_token_id,
            use_cache=True,              # Enable KV cache for faster generation
            repetition_penalty=1.0,      # Disable repetition penalty to save computation
            batch_size=1                 # Ensure we're using batch size 1
        )
        generated_text = result[0]["generated_text"]
        
        # Clear memory immediately after generation
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        json_part = apply_regex(generated_text, r'\{[^{]*?\}')

        try:
            data = json.loads(json_part) if json_part else {}
        except Exception as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            return None

        if not data:
            logger.error("No data extracted from LLM response")
            return Receipt()
    except torch.cuda.OutOfMemoryError:
        logger.error("CUDA out of memory during processing, falling back to CPU...")
        # Force CPU processing on OOM error
        torch.cuda.empty_cache()
        return process_with_cpu(logger, text)
    except Exception as e:
        logger.error(f"Error during receipt processing: {str(e)}")
        return None

    return Receipt(
        amount=data.get("amount"),
        description=data.get("description"),
        sender=data.get("sender"),
        receiver=data.get("receiver"),
        value=data.get("value")
    )

def process_with_cpu(logger: logging.Logger, text: str) -> Optional[Receipt]:
    """
    Fallback method to process text using CPU when GPU runs out of memory.
    
    This function provides a more memory-efficient way to process receipt text
    when GPU memory is insufficient, using the CPU with reduced model settings.
    
    Args:
        logger (logging.Logger): Logger for recording processing information
        text (str): Text extracted from receipt image
        
    Returns:
        Optional[Receipt]: A Receipt object with structured data, or None if processing failed
    """
    logger.info("Processing receipt text using CPU...")
    try:
        # Force CPU
        with torch.device("cpu"):
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            # Load model and tokenizer directly for more control over memory
            tokenizer = AutoTokenizer.from_pretrained("google/gemma-3-1b-it")
            model = AutoModelForCausalLM.from_pretrained(
                "google/gemma-3-1b-it",
                torch_dtype=torch.float32,  # Use float32 on CPU
                low_cpu_mem_usage=True
            )
            
            # Process in smaller chunks with smarter truncation
            max_cpu_length = 2000  # Even more conservative limit for CPU processing
            
            if len(text) > max_cpu_length:
                # Smart truncation: keep beginning (60%) and end (40%) of the text
                beginning = text[:int(max_cpu_length * 0.6)]
                end = text[-(int(max_cpu_length * 0.4)):]
                truncated_text = beginning + end
                logger.info(f"Further truncated text to {len(truncated_text)} chars for CPU processing")
                text = truncated_text
                
            formatted_prompt = PROMPT.format(text=text)
            inputs = tokenizer(formatted_prompt, return_tensors="pt")
            
            # Generate with minimal settings
            outputs = model.generate(
                inputs["input_ids"], 
                max_new_tokens=50,
                do_sample=False,
                num_return_sequences=1
            )
            
            generated_text = tokenizer.decode(outputs[0])
            json_part = apply_regex(generated_text, r'\{[^{]*?\}')
            
            try:
                data = json.loads(json_part) if json_part else {}
            except Exception as e:
                logger.error(f"Failed to parse JSON from CPU LLM response: {e}")
                return None
                
            return Receipt(
                amount=data.get("amount"),
                description=data.get("description"),
                sender=data.get("sender"),
                receiver=data.get("receiver"),
                value=data.get("value")
            )
    except Exception as e:
        logger.error(f"CPU processing failed: {str(e)}")
        return None
