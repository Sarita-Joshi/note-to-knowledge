import uuid
import asyncio
from fastapi import FastAPI, Form, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor

from rag_pipeline import RagPipeline

app = FastAPI()
graphs: Dict[str, RagPipeline] = {}
executor = ThreadPoolExecutor(max_workers=10)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class QueryRequest(BaseModel):
    question: str

class Triplet(BaseModel):
    source: str
    source_type: str
    source_desc: str
    target: str
    target_type: str
    target_desc: str
    relation: str
    relation_desc: str

class TripletResponse(BaseModel):
    triplets: List[Triplet]

class Node(BaseModel):
    id: str
    type: str
    description: Optional[str]

class Edge(BaseModel):
    source: str
    target: str
    label: str
    description: Optional[str]

class GraphResponse(BaseModel):
    nodes: List[Node]
    edges: List[Edge]

# Root check
@app.get("/", response_model=str)
def root():
    return "GraphRAG API is running. Use /query to ask questions or /triplets to get the knowledge graph triplets."

# Background-safe helpers
async def run_in_thread(fn, *args):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, fn, *args)

# Query endpoint
@app.post("/query", response_model=str)
async def query(question: QueryRequest, graph_id: str = "default"):
    if graph_id not in graphs:
        raise HTTPException(status_code=404, detail="Graph ID not found.")
    try:
        answer = await run_in_thread(graphs[graph_id].chat, question.question)
        return answer
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Triplets
@app.get("/triplets", response_model=TripletResponse)
async def get_triplets(graph_id: str = "default"):
    if graph_id not in graphs:
        raise HTTPException(status_code=404, detail="Graph ID not found.")

    try:
        triplets = await run_in_thread(graphs[graph_id].get_triplets)
        triplet_list = [
            Triplet(
                source=t[0][0].name,
                source_type=t[0][0].label,
                source_desc=t[0][0].properties.get("entity_description", ""),
                target=t[0][2].name,
                target_type=t[0][2].label,
                target_desc=t[0][2].properties.get("entity_description", ""),
                relation=t[0][1].label or "related_to",
                relation_desc=t[0][1].properties.get("relation_description", "")
            ) for t in triplets
        ]
        return TripletResponse(triplets=triplet_list)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Graph data
@app.get("/graph", response_model=GraphResponse)
async def get_graph(graph_id: str = "default"):
    if graph_id not in graphs:
        raise HTTPException(status_code=404, detail="Graph ID not found.")

    try:
        graph = await run_in_thread(graphs[graph_id].get_graph_json)
        return GraphResponse(nodes=graph['nodes'], edges=graph['edges'])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Upload
def build_pipeline_and_graph(graph_id: str, contents: str):
    pipeline = RagPipeline(graph_id=graph_id, text=contents)
    return pipeline

@app.post("/upload", response_model=str)
async def upload_document(
    graph_id: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None)
):
    try:
        if file:
            contents = file.file.read().decode("utf-8")
        elif text:
            contents = text
        else:
            raise HTTPException(status_code=400, detail="No document or text provided.")

        if not graph_id:
            graph_id = "graph_" + uuid.uuid4().hex[:8]

        pipeline = await run_in_thread(build_pipeline_and_graph, graph_id, contents)
        graphs[graph_id] = pipeline

        return f"✅ Document uploaded and graph built with ID: {graph_id}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Reset
@app.delete("/reset", response_model=str)
async def reset_graph(graph_id: str):
    if graph_id in graphs:
        del graphs[graph_id]
        return f"Graph {graph_id} has been reset."
    else:
        raise HTTPException(status_code=404, detail="Graph ID not found.")

# Dev mode
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
