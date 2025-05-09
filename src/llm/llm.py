from entities.receipt import Receipt
from llm.prompt import PROMPT
from utils.text import apply_regex
from transformers import pipeline
import torch
import re
import json

def get_pipeline():
    return pipeline(
        "text-generation", 
        model="google/gemma-3-1b-it", 
        device="cuda", 
        torch_dtype=torch.bfloat16
    )

def llm_parse_text_to_receipt(logger, text):
    pipe = get_pipeline()
    formatted_prompt = PROMPT.format(text=text)
    result = pipe(formatted_prompt, max_new_tokens=100)
    generated_text = result[0]["generated_text"]
    
    json_part = apply_regex(generated_text, r'\{[^{]*?\}')

    try:
        data = json.loads(json_part)
    except Exception as e:
        logger.error(f"Failed to parse JSON from LLM response: {e}")
        return None

    if not data:
        logger.error("No data extracted from LLM response")
        return Receipt()

    return Receipt(
        amount=data.get("amount"),
        description=data.get("description"),
        sender=data.get("sender"),
        receiver=data.get("receiver"),
        value=data.get("value")
    )
