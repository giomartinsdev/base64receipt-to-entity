PROMPT = '''
LOCALE:PT_BR

You are an expert at extracting specific information from text. Your task is to carefully read the provided receipt text and identify the following information:
- sender: the person sending/initiating the payment
- receiver: the person receiving the payment 
- amount: the monetary amount transferred (KEEP EXACT FORMAT as in text)
- value: same as amount, but as a string with original formatting
- description: the purpose or description of the transaction

Based on the information extracted, generate a JSON string containing ONLY the following keys and their corresponding values: "sender", "receiver", "amount", "value", and "description". For the monetary values:
- KEEP THE EXACT FORMAT as it appears in the text, including currency symbol
- DO NOT convert to decimal format
- Make sure it's a STRING with the ORIGINAL formatting (e.g., "R$ 1,58") be aware of the commas and dots
- DO NOT PICK UP THE DOCUMENT, 09438209 IS NOT a Value

Here is the receipt text:
{text}

Remember, your output should be ONLY ONE JSON string. Do not include any additional text, explanations, or formatting.
'''
