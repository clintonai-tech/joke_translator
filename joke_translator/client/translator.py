"""
Module for handling joke translations using various translation services.
"""

import os
import asyncio
import openai
from typing import Optional
import deepl

class TranslatorService:
    """Handles translations using various translation services."""
    
    def __init__(self):
        # Initialize OpenAI client if API key is available
        openai_key = os.getenv("OPENAI_API_KEY")
        print(f"Initializing OpenAI client with key: {'present' if openai_key else 'missing'}")
        self.gpt_client = openai.AsyncOpenAI(api_key=openai_key) if openai_key else None
        if not self.gpt_client:
            print("Failed to initialize OpenAI client - missing API key")
        
        # Initialize DeepL client if API key is available
        deepl_key = os.getenv("DEEPL_API_KEY")
        print(f"Initializing DeepL client with key: {'present' if deepl_key else 'missing'}")
        self.deepl_client = deepl.Translator(deepl_key) if deepl_key else None
        if not self.deepl_client:
            print("Failed to initialize DeepL client - missing API key")
        
    async def translate_with_gpt(self, text: str, target_lang: str) -> Optional[str]:
        """Translate text using GPT-4."""
        if not self.gpt_client:
            print("GPT client not initialized")
            return None
            
        try:
            print(f"Translating with GPT-4: text='{text}', target_lang='{target_lang}'")
            response = await self.gpt_client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": f"You are a translator. Translate the following text to {target_lang}. "
                              "Maintain the humor and cultural context where possible. "
                              "Only respond with the translation, nothing else."
                }, {
                    "role": "user",
                    "content": text
                }],
                max_tokens=200,
                temperature=0.3
            )
            translation = response.choices[0].message.content.strip()
            print(f"GPT-4 translation result: {translation}")
            return translation
        except Exception as e:
            print(f"Error translating with GPT-4: {e}")
            return None
    
    async def translate_with_deepl(self, text: str, target_lang: str) -> Optional[str]:
        """Translate text using DeepL."""
        if not self.deepl_client:
            print("DeepL client not initialized")
            return None
            
        try:
            print(f"Translating with DeepL: text='{text}', target_lang='{target_lang}'")
            # Run DeepL translation in a thread pool since it's synchronous
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.deepl_client.translate_text(
                    text=text,
                    target_lang=target_lang
                )
            )
            print(f"DeepL translation result: {result.text}")
            return result.text
        except Exception as e:
            print(f"Error translating with DeepL: {e}")
            return None
    
    async def translate(self, text: str, target_lang: str, service: str = "gpt") -> Optional[str]:
        """Translate text using the specified service."""
        if service == "gpt":
            return await self.translate_with_gpt(text, target_lang)
        elif service == "deepl":
            return await self.translate_with_deepl(text, target_lang)
        else:
            raise ValueError(f"Unsupported translation service: {service}") 