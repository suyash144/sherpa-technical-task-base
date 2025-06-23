# Sherpa Technical Task
Welcome!
You’re receiving an MVP that already works end-to-end. Your goal is to extend or improve it in any way that excites you, as long as the changes showcase applied AI skills. Go deep on one idea or sprinkle enhancements across layers - the choice is yours.

## Deliverables
1. Fully working codebase. We have tried to make this as easy as possible by setting up initial docker containers with persistent volumes. Depending on the changes you make to the environment, you may need to change this. 
| Note: If we cannot run your submission, we will not go out of our own way to resolve any environment issues
2. `explanations.md` A file that contains a detailed overview of some of the kley decision you made, explanataions of why you made them, and any challenged you faced along the way. This will also be a good opportunity for you to explain how you would have imprived the solution had you had more time.D

---
1. What you’re starting with

Backend (Python / FastAPI)
- Chat endpoint
- Streams tokens to the client via Server-Sent Events.
- Injects document snippets from a local FAISS vector store (Retrieval-Augmented Generation).
- File-upload endpoint
- Accepts PDF, Word or TXT.
- Stores originals on a Docker volume and embeds chunked text.
- Conversation history endpoint
- Fully containerised; runs offline with docker compose up.

Frontend (React / TypeScript)
- Chat page with real-time streaming bubbles and a collapsible sidebar that lists past messages.
- Upload page to add new documents.
- Built with Vite + Tailwind/ShadCN and served as a static site from Nginx.
-Ready-to-run Dockerfile and a one-service docker-compose.yml.

You can run everything locally in two commands:

```bash
# backend
cd backend && docker compose up -d # served at http://localhost:8080

# frontend
cd frontend && docker compose up -d  # served at http://localhost:3000
```
---

2. Where you can take it from here

Below is a menu of optional directions. Pick one path and run hard, or mix several lighter tweaks—entirely up to you.

A. Tool-calling & Agents
- Integrate external APIs (e.g., stock quotes, web search).
- Add a sandboxed Python evaluator for on-the-fly calculations.
- Turn the existing RAG module into an on-demand “tool” the model chooses to call.
- Introduce a second “judge” model that checks or critiques answers before they reach the user.

B. Evaluation & Data Quality
- Create or synthesize a small Q-A dataset and build a retrieval-accuracy metric (precision/recall, MRR, etc.).
- Add a generation-quality rubric (tone, factuality) graded automatically by an LLM.

C. User-Experience Polish
- Inline, clickable citations inside the answer text.
- Conversation search across a user’s chat history.
- Voice input/output or image/OCR uploads for a multimodal feel.

D. System & Dev-Ops
- User authentication and per-user document storage.
- Observability dashboard (traces, metrics).
- Hybrid retrieval (BM25 + vectors) or a switch to pgvector/elasticsearch.
- Concurrency controls and cost/token accounting.

E. Research / ML-Ops Extras
- Automated prompt-tuning loop driven by eval results.
- Local model fallback or response-cache to reduce latency/cost.
- Active-learning pipeline that flags low-confidence answers for human review.

F. RAG Enhancements
- Modifying the ingest / indexing process to utilise things like metadata extraction which will help to improve user experience
- Modifying the search process to use alternative search strategies
- Adding a pre-processing step to user queries so we can understand a) whether we need to search the database or not and b) exactly what they are searching for
- Adding a re-ranking step t0 make search more performative
- OCR or Visual Indexing strategies to handle more complex document types

Feel free to propose anything not listed—creativity is part of the exercise.

---

3. Submission Checklist
	1.	Code committed in a branch or fork, with clear commit messages.
	2.	README explaining:
    - What you built and why you chose that path
    - How to run it (ideally still via Docker).
	- Any known limitations or next steps you’d tackle with more time.
	3.	(Optional) Short demo video or screenshots.

We’ll review both the functionality and the engineering decisions behind it, so please document thought-process trade-offs where relevant.

Good luck, and have fun building!