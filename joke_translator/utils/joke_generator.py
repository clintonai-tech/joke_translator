"""
Module for generating and managing jokes.
"""

import os
import json
import random
import openai
from typing import Tuple, Optional, List

class JokeGenerator:
    """Manages joke generation and storage."""
    
    def __init__(self):
        self.jokes = []
        self.used_jokes = set()
        self.joke_counter = 0
        
        # Initialize OpenAI client if API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        self.gpt_client = openai.OpenAI(api_key=api_key) if api_key else None
        
        # Check if we should use GPT-4 for jokes
        self.use_gpt4 = os.getenv("USE_GPT4_JOKES") == "1"
        
        if self.use_gpt4:
            if not self.gpt_client:
                print("Warning: GPT-4 mode enabled but no OpenAI API key found")
            else:
                print("Using GPT-4 for generating jokes")
                # Generate initial set of jokes
                self._generate_initial_jokes()
        else:
            # Load static jokes from file
            self.jokes_file = "jokes.json"
            self._load_jokes()
    
    def _load_jokes(self):
        """Load jokes from the JSON file."""
        try:
            if os.path.exists(self.jokes_file):
                with open(self.jokes_file, "r") as f:
                    self.jokes = json.load(f)
                print(f"Loaded {len(self.jokes)} jokes from file")
            else:
                print("No jokes file found, using default joke")
                self.jokes = ["Why did the programmer quit his job? Because he didn't get arrays!"]
        except Exception as e:
            print(f"Error loading jokes: {e}")
            self.jokes = ["Why did the programmer quit his job? Because he didn't get arrays!"]
    
    def _generate_initial_jokes(self):
        """Generate 50 jokes using GPT-4."""
        try:
            print("Generating 50 jokes with GPT-4...")
            all_jokes = []
            
            # Generate jokes in batches of 10
            for i in range(5):
                print(f"Generating batch {i + 1}/5...")
                response = self.gpt_client.chat.completions.create(
                    model="gpt-4",
                    messages=[{
                        "role": "system",
                        "content": "You are a comedian. Generate 10 short, clean, and funny jokes. "
                                 "Format your response as a numbered list, one joke per line. "
                                 "Each joke should be concise, unique, and family-friendly. "
                                 "Do not repeat any jokes from previous responses."
                    }],
                    max_tokens=500,
                    temperature=0.7
                )
                
                # Parse the response into individual jokes
                content = response.choices[0].message.content.strip()
                # Split into lines and remove empty lines
                joke_lines = [line.strip() for line in content.split('\n') if line.strip()]
                # Remove numbering and any extra whitespace
                jokes = [line.split('.', 1)[1].strip() if '.' in line else line for line in joke_lines]
                all_jokes.extend(jokes)
            
            if all_jokes:
                self.jokes = all_jokes
                print(f"Successfully generated {len(self.jokes)} jokes")
            else:
                print("Failed to generate jokes, using default joke")
                self.jokes = ["Why did the programmer quit his job? Because he didn't get arrays!"]
            
        except Exception as e:
            print(f"Error generating jokes: {e}")
            self.jokes = ["Why did the programmer quit his job? Because he didn't get arrays!"]
    
    async def generate_joke_gpt(self) -> Optional[str]:
        """Generate a new joke using GPT-4."""
        if not self.gpt_client:
            return None
            
        try:
            response = await self.gpt_client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": "You are a comedian. Generate a short, clean, and funny joke."
                }],
                max_tokens=100,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating joke with GPT-4: {e}")
            return None
    
    def get_joke(self) -> Tuple[int, str]:
        """Get a random joke and its ID."""
        if not self.jokes:
            return self.joke_counter, "Why did the programmer quit his job? Because he didn't get arrays!"
            
        available_jokes = [joke for joke in self.jokes if joke not in self.used_jokes]
        if not available_jokes:
            # If all jokes have been used, reset the used_jokes set
            self.used_jokes.clear()
            available_jokes = self.jokes
            
        joke = random.choice(available_jokes)
        self.used_jokes.add(joke)
        self.joke_counter += 1
        
        return self.joke_counter, joke
    
    def add_joke(self, joke: str) -> bool:
        """Add a new joke to the collection."""
        if joke and joke not in self.jokes:
            self.jokes.append(joke)
            self._save_jokes()
            return True
        return False
    
    def remove_joke(self, joke: str) -> bool:
        """Remove a joke from the collection."""
        if joke in self.jokes:
            self.jokes.remove(joke)
            self.used_jokes.discard(joke)
            self._save_jokes()
            return True
        return False
    
    def _save_jokes(self):
        """Save jokes to the JSON file."""
        try:
            with open(self.jokes_file, "w") as f:
                json.dump(self.jokes, f, indent=2)
        except Exception as e:
            print(f"Error saving jokes: {e}") 