
# Graph RAG: From Notes to Knowledge Graphs

This project turns unstructured notes into a queryable knowledge graph using LLMs. Instead of retrieving text chunks based on vector similarity, it leverages graph traversal and entity relationships to support multi-hop reasoning.

The system includes:
- A FastAPI backend for document ingestion and graph-based retrieval
- A React frontend with D3-based graph visualization
- A chat interface grounded entirely in knowledge graph context

## Demo



## Features

- Upload and parse raw text or notes
- Extract (Entity A) —[Relation]→ (Entity B) triples using LLM prompts
- Construct a live, visual knowledge graph
- Query the graph using a chat interface (no vector database required)
- Modular API-first backend designed for reuse in agents or bots

## Tech Stack

| Layer        | Technology            |
|--------------|------------------------|
| Frontend     | React, TailwindCSS     |
| Backend      | FastAPI (Python)       |
| RAG Engine   | LlamaIndex (Graph RAG) |
| Visualization| D3.js                  |
| Future Plans | Neo4j, spaCy, Hybrid RAG |

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Sarita-Joshi/note-to-knowledge.git
cd note-to-knowledge
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Backend Dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Run the Backend (FastAPI)

```bash
python app.py
```

### 5. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

Create a `.env` file in the backend root directory with the important keys like

```env
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

## API Endpoints

See `app.py` for the following endpoints:

- `POST /upload` — Ingest text or notes
- `GET /graph` — Retrieve graph nodes and edges
- `GET /chat` — Query graph via LLM-backed reasoning

Auto-generated Swagger docs coming soon.

## Known Issues

### Async Handling in LlamaIndex

Some LlamaIndex methods are asynchronous internally, which may cause issues with FastAPI's sync/async routing.

Common error:

```
RuntimeWarning: coroutine '...' was never awaited
```

Workarounds attempted:
- Wrapping calls with `asyncio.run()`
- Background task queues
- Refactoring into sync-friendly wrappers

Contributions welcome if you’ve solved this more cleanly.

## Roadmap

- [ ] Neo4j support for persistent graph storage
- [ ] Entity resolution via spaCy or sentence embeddings
- [ ] Hybrid Graph + Vector RAG
- [ ] Feedback loop to validate or revise extracted triples
- [ ] Graph memory integration for agent workflows

## Contribution

Contributions are welcome. To get started:

```bash
git checkout -b feature-name
# make your changes
git commit -m "Add feature"
git push origin feature-name
```

Then open a pull request.

Source: https://github.com/Sarita-Joshi/note-to-knowledge

## License

MIT License

## Author

Built as part of a personal Mini Project Series focused on building E2E Applciations with AI, LLMs, and data-driven systems.
