"""
LLM Integration Service for Gemini API
"""
import google.generativeai as genai
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google's Gemini API"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-pro"):
        """
        Initialize Gemini service
        
        Args:
            api_key: Gemini API key
            model_name: Model name to use
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name
    
    def generate_summary(
        self,
        text: str,
        max_tokens: int = 2000
    ) -> dict:
        """
        Generate structured summary of research paper
        
        Args:
            text: Document text
            max_tokens: Maximum tokens for generation
            
        Returns:
            Dictionary with summary sections
        """
        try:
            prompt = f"""
            Analyze the following research paper and provide a structured summary with these sections:
            1. Title & Authors - Extract the title and author information
            2. Abstract - Summarize the abstract or main overview
            3. Problem Statement - What problem does this paper address?
            4. Methodology - How did they conduct their research?
            5. Key Results - What were the main findings?
            6. Conclusion - What are the conclusions?
            
            Format your response as a JSON with keys: title_and_authors, abstract, problem_statement, methodology, key_results, conclusion
            Each key should have nested "title" and "content" fields.
            
            Research Paper:
            {text[:5000]}  # Limit to first 5000 chars for API
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse response
            import json
            try:
                summary_data = json.loads(response.text)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                summary_data = self._parse_summary_fallback(response.text)
            
            return summary_data
        
        except Exception as e:
            logger.error(f"Error generating summary with Gemini: {e}")
            raise
    
    def answer_question(
        self,
        question: str,
        context: str,
        max_tokens: int = 1000
    ) -> str:
        """
        Answer question based on provided context
        
        Args:
            question: User's question
            context: Relevant document context
            max_tokens: Maximum tokens for answer
            
        Returns:
            Generated answer
        """
        try:
            prompt = f"""
            Based on the following research paper context, please answer the question.
            Provide a clear, concise answer.
            
            Context:
            {context}
            
            Question: {question}
            
            Answer:
            """
            
            response = self.model.generate_content(prompt)
            return response.text
        
        except Exception as e:
            logger.error(f"Error answering question with Gemini: {e}")
            raise
    
    @staticmethod
    def _parse_summary_fallback(text: str) -> dict:
        """
        Fallback parser for summary if JSON parsing fails
        
        Args:
            text: Response text
            
        Returns:
            Parsed summary dictionary
        """
        return {
            "title_and_authors": {"title": "Title & Authors", "content": "Unable to parse"},
            "abstract": {"title": "Abstract", "content": "Unable to parse"},
            "problem_statement": {"title": "Problem Statement", "content": "Unable to parse"},
            "methodology": {"title": "Methodology", "content": "Unable to parse"},
            "key_results": {"title": "Key Results", "content": "Unable to parse"},
            "conclusion": {"title": "Conclusion", "content": "Unable to parse"}
        }
