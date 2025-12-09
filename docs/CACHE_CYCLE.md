# Cache Cycle in the Research Assistant

This document explains how caching and conversational memory flow through the system to make the chatbot faster and more familiar while keeping costs low.

## Components
- **Response cache (`SimpleTTLCache`)**: Short-term memoization of answers per `(document_id, question)` pair. Lives in-process with a TTL and size bound.
- **Conversation memory (`MemoryStore`)**: Per-conversation sliding window of the last N turns (user + assistant) with TTL eviction. Keyed by `conversation_id` (or document_id + client IP fallback).
- **Vector stores**:
  - `documents_collection`: fine-grained chunks from the PDF.
  - `summaries_collection`: section-level embeddings of the structured summary (Title/Authors, Abstract, Problem, Methodology, Key Results, Conclusion) for fast familiarization.

## Request/Response Cycle (QA)
1) **Question received** (`/qa/ask`):
	- Derive `conversation_id` (client-supplied or fallback) and append the user turn into `MemoryStore`.
2) **Response cache lookup**:
	- Build cache key = `document_id :: question`.
	- If hit → return cached answer; also append the assistant reply to memory; skip retrieval/LLM; done.
3) **Retrieval** (if no cache hit):
	- Embed question (SentenceTransformers all-mpnet-base-v2).
	- Query `documents_collection` for top-k chunks scoped to `document_id`.
	- Query `summaries_collection` for top-k summary sections scoped to `document_id`.
	- Merge chunk + summary contexts.
4) **Prompt assembly**:
	- Build prompt with: system instructions, conversation memory (recent turns), merged context, and user question.
5) **LLM generation**:
	- Gemini produces the answer.
6) **Post-process**:
	- Compute a simple confidence (1 - avg distance of retrieved vectors, clamped 0..1).
	- Persist assistant turn into `MemoryStore`.
	- Write the full `ChatResponse` into `SimpleTTLCache` under the cache key.
7) **Return**: answer + sources (merged context) + confidence.

## Upload Cycle (documents)
1) Extract text → chunk → embed chunks → store in `documents_collection`.
2) Generate structured summary → embed each section → store in `summaries_collection`.
3) Return summary + metadata to the client.

## Eviction & Freshness
- **Response cache TTL**: short (default 10 minutes) to balance speed and staleness.
- **Memory TTL**: longer (default 24 hours) to keep session familiarity; capped to last N turns.
- **Vector stores**: durable; re-uploading a PDF refreshes both chunk and summary embeddings.

## Benefits
- **Speed**: Cache hits avoid retrieval + LLM calls.
- **Familiarity**: Memory keeps conversational context; summary vectors provide high-level grounding.
- **Cost control**: Reduced LLM invocations on repeat questions; small contexts via summaries lower prompt size.
- **Quality**: Combined retrieval (chunks + summaries) balances detail and overview, reducing shallow or off-target answers.
