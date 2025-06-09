import uuid
import asyncio
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
app = FastAPI()
from rag_pipeline import RagPipeline
# Initialize the RAG pipeline
graphs: Dict[str, RagPipeline] = {}

# CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/", response_model=str)
def root():
    """Root endpoint to check if the server is running."""
    return "GraphRAG API is running. Use /query to ask questions or /triplets to get the knowledge graph triplets."

@app.post("/query", response_model=str)
async def query(question: QueryRequest, graph_id: str = "default"):
    """Endpoint to query the knowledge graph with a natural language question."""

    if graph_id not in graphs:
        raise HTTPException(status_code=404, detail="Graph ID not found.")
    try:
        answer = graphs[graph_id].chat(question.question)
        return answer
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/triplets", response_model = TripletResponse)
async def get_triplets(graph_id: str = "default"):

    if graph_id not in graphs:
        raise HTTPException(status_code=404, detail="Graph ID not found.")

    try:
        triplets = graphs[graph_id].get_triplets()
        triplet_list = []
        for triplet in triplets:
            source = triplet[0][0]
            edge = triplet[0][1]
            target = triplet[0][2]

            triplet_list.append(Triplet(
                source = source.name,
                source_type = source.label,
                source_desc = source.properties.get("entity_description", ""),
                target = target.name,
                target_type = target.label,
                target_desc = target.properties.get("entity_description", ""),
                relation = edge.label or "related_to",
                relation_desc = edge.properties.get("relation_description", "")
            ))
        
        return TripletResponse(triplets=triplet_list)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/graph", response_model=GraphResponse)
async def get_graph(graph_id: str = "default"):
    """Endpoint to get the knowledge graph in JSON format."""
    if graph_id not in graphs:
        raise HTTPException(status_code=404, detail="Graph ID not found.")

    try:
        
        graph = graphs[graph_id].get_graph_json()
        return GraphResponse(nodes=graph['nodes'], edges=graph['edges'])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

   
from fastapi import File, UploadFile

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
            
        if not graph_id or graph_id not in graphs:
            graph_id = "graph_" + uuid.uuid4().hex[:8]
            graphs[graph_id] = RagPipeline(graph_id=graph_id, text=contents)
        
        graphs[graph_id].build_graph_from_text(contents)
        return f"✅ Document uploaded and graph built with ID: {graph_id}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/reset", response_model=str)
async def reset_graph(graph_id: str):
    if graph_id in graphs:
        del graphs[graph_id]
        return f"Graph {graph_id} has been reset."
    else:
        raise HTTPException(status_code=404, detail="Graph ID not found.")

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)