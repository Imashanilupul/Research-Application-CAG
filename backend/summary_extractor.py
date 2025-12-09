"""
Summary extraction from first page of research papers
"""

import json
from typing import Dict, Optional
import google.generativeai as genai
import config


def generate_summary_from_first_page(first_page_text: str) -> Dict:
    """
    Generate structured summary from the first page of a research paper.
    This approach is more effective as the first page typically contains:
    - Title & Authors
    - Abstract
    - Introduction (which includes Problem Statement)
    """
    
    prompt = f"""You are a research paper analyzer. Based on the first page of a research paper, extract the following information and return ONLY valid JSON (no markdown, no explanations).

Extract these sections:
1. Title & Authors - The paper title and author names
2. Abstract - A 2-3 sentence summary of the paper's objective
3. Problem Statement - The main problem or challenge being addressed
4. Methodology - The approach/method used (if mentioned)
5. Key Results - Main findings or outcomes (if mentioned)
6. Conclusion - Conclusion or implications (if mentioned)

Return this exact JSON structure:
{{
  "title_and_authors": {{
    "title": "Title & Authors",
    "content": "[Paper title and author names. If not found, write: Not clearly stated.]"
  }},
  "abstract": {{
    "title": "Abstract",
    "content": "[2-3 sentence abstract. If not found, write: Not clearly stated.]"
  }},
  "problem_statement": {{
    "title": "Problem Statement",
    "content": "[Main problem being addressed. If not found, write: Not clearly stated.]"
  }},
  "methodology": {{
    "title": "Methodology",
    "content": "[Research methodology/approach. If not found, write: Not clearly stated.]"
  }},
  "key_results": {{
    "title": "Key Results",
    "content": "[Main findings/results. If not found, write: Not clearly stated.]"
  }},
  "conclusion": {{
    "title": "Conclusion",
    "content": "[Conclusion/implications. If not found, write: Not clearly stated.]"
  }}
}}

IMPORTANT RULES:
- Return ONLY the JSON object, no other text
- Each content field should be 1-3 complete sentences
- If a section is not found on the first page, write: "Not clearly stated."
- Do not include markdown code blocks or formatting
- Do not include page numbers or headers

First page content:
{first_page_text}
"""
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        # Parse JSON
        summary = json.loads(response_text)
        
        # Validate structure
        required_keys = ["title_and_authors", "abstract", "problem_statement", "methodology", "key_results", "conclusion"]
        for key in required_keys:
            if key not in summary:
                summary[key] = {"title": key.replace("_", " ").title(), "content": "Not clearly stated."}
        
        return summary
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        return _get_default_summary()
    except Exception as e:
        print(f"Error generating summary: {e}")
        return _get_default_summary()


def _get_default_summary() -> Dict:
    """Return default summary structure when extraction fails"""
    return {
        "title_and_authors": {"title": "Title & Authors", "content": "Not clearly stated."},
        "abstract": {"title": "Abstract", "content": "Not clearly stated."},
        "problem_statement": {"title": "Problem Statement", "content": "Not clearly stated."},
        "methodology": {"title": "Methodology", "content": "Not clearly stated."},
        "key_results": {"title": "Key Results", "content": "Not clearly stated."},
        "conclusion": {"title": "Conclusion", "content": "Not clearly stated."},
    }
