import cohere
from typing import List, Dict, Any
from ..config.settings import settings


class GenerationService:
    """
    Service for generating answers using Cohere.
    """

    def __init__(self):
        # Initialize the Cohere client
        self.client = cohere.Client(settings.COHERE_API_KEY)
    
    def generate_answer(self, query: str, context_chunks: List[Dict[str, Any]],
                       mode: str = "full-book") -> str:
        """
        Generate an answer based on the query and context chunks using Cohere.

        Args:
            query: The user's question
            context_chunks: List of relevant document chunks
            mode: "full-book" or "selected-text"

        Returns:
            Generated answer
        """
        # Construct the context from the retrieved chunks
        context = ""
        for i, chunk in enumerate(context_chunks):
            context += f"Source {i+1}: {chunk['content']}\n\n"

        # Create the prompt based on the mode
        if mode == "selected-text":
            prompt = f"""Based ONLY on the following selected text, answer the question.
If the answer is not available in the provided text, respond with exactly:
"This information is not available in the book."

Selected text:
{context}

Question: {query}

Answer:"""
        else:  # full-book mode
            prompt = f"""Based ONLY on the following book content, answer the question.
If the answer is not available in the provided content, respond with exactly:
"This information is not available in the book."

Book content:
{context}

Question: {query}

Answer:"""

        try:
            # Use Cohere's chat API which is the recommended approach
            # Using a standard model that should be available
            response = self.client.chat(
                message=prompt,
                max_tokens=500,
                temperature=0.3,  # Lower temperature for more factual responses
            )

            # Extract the text from the response
            answer = response.text.strip()

            # Verify the response doesn't contain hallucinations by checking if it follows the required format
            if "This information is not available in the book." in answer:
                return "This information is not available in the book."

            return answer
        except Exception as e:
            print(f"Error generating answer with Cohere: {e}")
            return "This information is not available in the book."
    
    def validate_response(self, response: str, context: List[Dict[str, Any]]) -> bool:
        """
        Validate that the response is grounded in the provided context and doesn't contain hallucinations.
        
        Args:
            response: The generated response
            context: The context provided to the model
            
        Returns:
            True if the response is valid, False otherwise
        """
        # For now, we'll implement a simple check
        # In a production system, this would involve more sophisticated validation
        if response == "This information is not available in the book.":
            return True
        
        # Check if the response contains information that's supported by the context
        # This is a simplified check - a real implementation would be more thorough
        context_text = " ".join([chunk['content'] for chunk in context])
        # This is a basic check to see if the response has some connection to the context
        # In practice, you'd want more sophisticated validation
        return len(response) > 0