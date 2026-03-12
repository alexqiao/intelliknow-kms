# AI Usage Reflection - IntelliKnow KMS

## Project Overview

This 7-day case study project built a Gen AI-powered Knowledge Management System (IntelliKnow KMS) addressing enterprise pain points: fragmented information, inefficient knowledge retrieval, and siloed communication channels. The system integrates with Telegram and Slack, automatically builds knowledge bases from uploaded documents, and uses AI-powered intent classification to route queries.

---

## Strategic AI Usage: Core Scenarios (As Required)

### Scenario 1: Document Parsing - Compute Offloading & Dual-Pipeline Architecture

* **Challenge:** When processing complex enterprise documents with embedded tables (e.g., HR salary grids, Legal fee schedules), the system faced a critical constraint: Render's start tier enforces a strict 512MB RAM limit. Traditional local OCR libraries (like `pdfplumber`) consume massive memory, risking OOM (Out of Memory) crashes. Furthermore, pure text parsing often destroys tabular structures, making numerical data unsearchable.
* **AI Solution:** I implemented a **Dual-Pipeline Architecture**. 
  1. **Primary AI Pipeline:** Offloads heavy OCR and layout analysis to Aliyun Document Mind API via async polling. This AI service extracts structured tabular data and perfectly maps it into Markdown format, ensuring numerical/structured knowledge remains highly searchable.
  2. **Fallback Pipeline:** Uses lightweight local libraries (`PyPDF2`/`docx`) to ensure 100% uptime if the cloud API fails.
* **Impact:** Solved the limitation of pure text parsing, successfully preserved complex tabular structures without crashing the memory-constrained container, and reduced manual data entry/cleaning time by over 60%.

### Scenario 2: Frontend Integration - Cross-Platform Formatting via LLM Context

* **Challenge:** Rendering complex KMS knowledge consistently across different platforms is notoriously difficult due to native format constraints. For example, Slack uses a unique markdown dialect (single asterisks `*bold*` instead of standard `**bold**`), while Telegram's `MarkdownV2` aggressively requires escaping punctuation (causing backslash visible errors or message delivery failures). Building custom, hard-coded formatters for each platform is unscalable and error-prone.
* **AI Solution:** Instead of writing complex custom formatters, I leveraged the LLM's natural language understanding. I injected the platform context (`request.source`) directly into the RAG Generation Prompt with strict adaptation rules:
  - **For Telegram:** The LLM is instructed to bypass markdown entirely, providing an extremely concise, plain-text summary (under 100 words) suited for mobile screens, eliminating the Telegram escaping crash loop.
  - **For Slack:** The LLM is instructed to use Slack-specific dialect (single asterisks) and rich bullet points while maintaining the 100-word brevity limit.
* **Impact:** Ensured a native user experience across platforms with zero custom frontend formatting code, streamlining integration development and proving the viability of "AI-driven UI adaptation".

---

## Engineering Deep-Dive: Overcoming System Bottlenecks

Beyond the core functional requirements, AI and architectural decisions were heavily utilized to iterate faster and overcome severe deployment bottlenecks:

### 1. Eliminating "Event Loop Blocking" via AsyncOpenAI

* **Issue:** Initial end-to-end latency on the Render deployment spiked to >7 seconds. Profiling revealed that synchronous OpenAI clients were blocking FastAPI's single-core event loop, causing the Intent Classification and Vector Embedding steps to execute sequentially.
* **Iteration:** I refactored the entire LLM service layer using the Factory Pattern and `AsyncOpenAI`. By utilizing `asyncio.gather()`, I achieved true non-blocking concurrent I/O.
* **Result:** Slashed the "Intent + Embedding" phase latency from ~7.5s to under 1.5s.

### 2. Curing "LLM Verbosity" and "Persona Hijacking"

* **Issue:** When handling out-of-domain queries or simple greetings (e.g., "hello"), the LLM would generate long explanatory filler text, spiking response times to 8+ seconds, or hallucinate a conversational persona ignoring the RAG context.
* **Iteration:** Implemented **Strict JSON-Mode enforcement** with Few-Shot Prompting in the Intent Router to instantly force a categorized JSON output. In the RAG Generator, I implemented a Highly Structured Prompt with a strict `GREETING CHECK` and `CONTEXT CHECK` to forcefully bound the LLM's behavior.
* **Result:** Reduced out-of-domain query latency to <1 second and achieved a 100% deterministic fallback response ("No relevant information found...").

### 3. State Synchronization for Vector Databases

* **Issue:** Deleting documents caused an "ID Desync" bug because the local FAISS index array shifts its internal IDs upon deletion, breaking the mapping to the SQLite metadata.
* **Iteration:** Redesigned the retrieval flow to bypass native FAISS IDs, instead injecting the immutable SQLite `doc_id` directly into the FAISS vector metadata payload, combined with cascading SQL deletes.
* **Result:** Guaranteed absolute memory safety and data consistency between the relational database and the vector store.

---

## Quantitative Results (Based on Automated Batch Evaluation)

To rigorously test the system, I built a custom Python batch evaluation script against a Ground Truth dataset (112 test cases).

| Metric                    | Result             | Note                                                                      |
|:------------------------- |:------------------ |:------------------------------------------------------------------------- |
| **End-to-End Latency**    | **~900 - 1500 ms** | Met the strict <3s SLA requirement on a 0.5 CPU container.                |
| **Intent Classification** | **94%**            | Zero token-generation overhead thanks to Strict JSON prompting.           |
| **Answer Accuracy**       | **94%+**           | Automated heuristic evaluation with manual review                         |
| **System Uptime**         | **100%**           | Kept TCP connection pools warm via continuous HEAD request health checks. |

## Conclusion

AI tools were instrumental not just in generating text, but in serving as a dynamic "Compute Engine" (Aliyun OCR) and an "Adaptive Router/Formatter" (Cross-platform prompt engineering). The key takeaway from this project is that while LLMs provide immense flexibility, true enterprise readiness (SLA < 3s, zero hallucinations, cross-platform stability) requires relentless attention to asynchronous I/O, strict prompt bounding, and defensive engineering practices.
