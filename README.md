# Sherpa Technical Task

## 📌 Context

At Sherpa, we build AI-enabled software for management consulting and professional services firms. Our applications frequently process complex, unstructured data from documents such as PDFs, Word files, and presentations. Our solutions must be secure, scalable, and tailored for enterprise-grade reliability.

You’ve been provided with a fully-functional MVP—a chatbot integrated with Retrieval-Augmented Generation (RAG)—built using FastAPI (Python backend) and React (TypeScript frontend). 

> Note: We have provided an optional set of ~20 complex consulting documents for you to test the vector store with. If you would like to change this, or add new documents of different modalities, you are more than welcome to.


Your have 4 hours to enhance this chatbot by extending its functionality, performance, or user experience.

---

## 🚩 Objective

Your goal is to demonstrate your applied AI and engineering skills by making meaningful improvements to the provided MVP. You can choose to focus deeply on a single enhancement or implement several lighter improvements across multiple areas, depending on your interests and strengths.

We encourage creativity and practical innovation. Your enhancements should clearly showcase your technical decision-making, your approach to problem-solving, and your ability to handle real-world engineering trade-offs.

---

## 🛠️ What You’re Starting With

Backend (Python / FastAPI)
- Chat endpoint with streaming token responses via Server-Sent Events.
- Retrieval-Augmented Generation (RAG) integrated with a local FAISS vector store.
- File-upload endpoint supporting PDFs, Word documents, and TXT files.
- Persistent document storage using Docker volumes.
- Conversation history management.
- Fully containerized setup running locally via Docker Compose.

Frontend (React / TypeScript)
- Chat interface with real-time streaming chat bubbles.
- Sidebar displaying conversation history.
- Document upload page.
- Built with Vite, Tailwind, and ShadCN.
- Containerized deployment served statically via Nginx.

To run the provided solution:

### Backend
```bash
cd backend
```
1. Initial Set Up (Creating the volumes, blank .env and relevant instalations using UV)
```bash
./setup.sh
```
2. Build the Docker container
```bash
docker-compose build --no-cache
```
3. Run the docker container (available at http://localhost:8080)
```bash
docker-compose up
```

### Frontend
```bash
cd frontend
```
1. Install the relevant packages
```bash
npm install
```
2. Build the Docker container
```bash
docker-compose build --no-cache
```
3. Run the docker container (available at http://localhost:3000)
```bash
docker-compose up
```

---

## 🚀 Potential Enhancements

Below is a list of suggested directions you could pursue, grouped into thematic areas. You are free to choose from any of the below, or choose your own.

A. Tool-calling & Agents
- Integrate external APIs (e.g., finance, web search).
- Embed a sandboxed Python environment for real-time computations.
- Transform the RAG module into an on-demand tool invoked by the model.
- Introduce a “judge” model to validate or critique responses before delivery.

B. Evaluation & Data Quality
- Create or synthesize a QA dataset for retrieval evaluation metrics (precision/recall, MRR).
- Implement an automatic generation-quality evaluation using LLM-driven rubrics (factual accuracy, tone).
- Add in an Evals pipeline for the retrieval step using a set of benchmark data and Question-Document pairs

C. Search Strategies
- Implement query enrichment / pre-processing
- Introduce hybrid retrieval methods (BM25 combined with vector search) or alternative indexing (pgvector, Elasticsearch)
- Leverage ANN for improved search efficiency.
- Add in an additional re-ranking step that could be used to solve the "needle in a haystack" problem at large scale

D. ML-Ops & Research
- Automated prompt-tuning using feedback from evaluations.
- Add in user feedback that can be fed back to the model
- Utilise different models or try out newer features in the model APIs

E. Advanced RAG Enhancements
- Upgrade ingestion/indexing processes with metadata extraction for improved retrieval.
- Experiment with advanced search strategies and query preprocessing.
- Implement document re-ranking strategies for improved search quality.
- Integrate OCR and visual indexing capabilities for richer document types.

---

## ✅ Deliverables

Essential
	1.	A fully functional and clearly organized repository fork with comprehensible commit messages.
	2.	Explanations.md containing:
- An overview of your enhancements.
- Justification for chosen solutions and their implementation.
- Clear setup instructions (extending the existing Docker preferred).
> Warning: I will not be going out of my way to resolve environment and dependency issues when trying to run your solution locally. We understand that DevOps can be difficult, so we will give candidates 1 extra chance to fix env issues if we can't build your solution first time.
- Any limitations or future improvement areas identified.

Optional (but encouraged)
- Brief demo video or illustrative screenshots demonstrating key features.

---

## 🚨 Evaluation Criteria

We will assess your submission based on:
- Functionality and robustness of your enhancements.
- Quality and clarity of engineering decisions documented.
- Practicality and creativity in solving real-world problems.
- Code quality, readability, and maintainability.

Remember, we’re not necessarily looking for a fully-polished enterprise-grade solution, but rather evidence of thoughtful, practical problem-solving and clear communication of your engineering choices.

After reviewing your submission, successful candidates will be invited to a follow-up meeting to discuss your solution, thought process, and how you envision scaling your enhancements in a production environment.

Good luck, and enjoy the challenge!

> **Disclaimer:** No code submitted by any candidate will be used by Sherpa in development or production scenarios. 