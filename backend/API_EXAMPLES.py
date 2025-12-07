"""
API Request/Response Examples and Documentation
"""

# Example 1: Upload PDF
upload_example = {
    "method": "POST",
    "endpoint": "/documents/upload",
    "description": "Upload a research paper PDF",
    "request": {
        "type": "multipart/form-data",
        "file": "research_paper.pdf (binary)"
    },
    "response": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "filename": "research_paper.pdf",
        "upload_date": "2024-01-15T10:30:00",
        "file_size": 2048576,
        "summary": {
            "title_and_authors": {
                "title": "Title & Authors",
                "content": "A Study on Machine Learning..."
            },
            "abstract": {
                "title": "Abstract",
                "content": "This paper investigates..."
            },
            "problem_statement": {
                "title": "Problem Statement",
                "content": "Current approaches fail to..."
            },
            "methodology": {
                "title": "Methodology",
                "content": "We propose a novel approach..."
            },
            "key_results": {
                "title": "Key Results",
                "content": "Our method achieves 95% accuracy..."
            },
            "conclusion": {
                "title": "Conclusion",
                "content": "This work demonstrates..."
            }
        },
        "status": "success"
    }
}

# Example 2: Ask Question
question_example = {
    "method": "POST",
    "endpoint": "/qa/ask",
    "description": "Ask a question about a research paper",
    "request": {
        "document_id": "550e8400-e29b-41d4-a716-446655440000",
        "question": "What methodology was used in this study?",
        "top_k": 3
    },
    "response": {
        "document_id": "550e8400-e29b-41d4-a716-446655440000",
        "question": "What methodology was used in this study?",
        "answer": "The study employed a novel deep learning approach with transformer architecture. The methodology consists of three main phases: data preprocessing, model training, and evaluation. The authors used a custom dataset of 100,000 samples...",
        "sources": [
            "The study employed a novel deep learning approach...",
            "Data preprocessing involved normalization and augmentation...",
            "Model training was conducted using the Adam optimizer..."
        ],
        "confidence": 0.87
    }
}

# Example 3: List Documents
list_example = {
    "method": "GET",
    "endpoint": "/documents/list",
    "description": "List all uploaded documents",
    "response": {
        "documents": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "filename": "research_paper1.pdf",
                "upload_date": "2024-01-15T10:30:00",
                "file_size": 2048576,
                "chunk_count": 45,
                "status": "processed"
            },
            {
                "id": "660e8400-e29b-41d4-a716-446655440001",
                "filename": "research_paper2.pdf",
                "upload_date": "2024-01-15T11:00:00",
                "file_size": 1535897,
                "chunk_count": 38,
                "status": "processed"
            }
        ],
        "total": 2
    }
}

# Example 4: Delete Document
delete_example = {
    "method": "DELETE",
    "endpoint": "/documents/{document_id}",
    "description": "Delete a document",
    "response": {
        "status": "success",
        "message": "Document 550e8400-e29b-41d4-a716-446655440000 deleted successfully"
    }
}

if __name__ == "__main__":
    import json
    
    examples = {
        "upload": upload_example,
        "question": question_example,
        "list": list_example,
        "delete": delete_example
    }
    
    print(json.dumps(examples, indent=2, default=str))
