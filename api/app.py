import os
import uuid
import asyncio
from fastapi import FastAPI, Form, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional

from concurrent.futures import ThreadPoolExecutor
from llama_index_server.rag_pipeline import RagPipeline
from models import *
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


# Upload
def build_pipeline_and_graph(graph_id: str, contents: str=None):
    pipeline = RagPipeline(graph_id=graph_id, text=contents)
    return pipeline

import os
async def check_in_cache(graph_id: str,) -> bool:
    if graph_id in graphs:
        return True
    base_dir = os.path.join("cached_graphs", graph_id)
    if os.path.exists(base_dir):
        pipeline = await run_in_thread(build_pipeline_and_graph, graph_id)
        graphs[graph_id] = pipeline
        return True
    return False


# Root check
@app.get("/", response_model=str)
def root():
    return "GraphRAG API is running."

# Background-safe helpers
async def run_in_thread(fn, *args):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, fn, *args)

# Query endpoint
@app.get("/query", response_model=str)
async def query(question: str, graph_id: str = "default"):
    if not await check_in_cache(graph_id):
        raise HTTPException(status_code=404, detail="Graph ID not found.")
    try:
        answer = await run_in_thread(graphs[graph_id].query, question)
        return answer
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Chat endpoint
@app.get("/chat", response_model=str)
async def chat(question: str, graph_id: str = "default"):
    if not await check_in_cache(graph_id):
        raise HTTPException(status_code=404, detail="Graph ID not found.")
    try:
        answer = await run_in_thread(graphs[graph_id].chat, question)
        return answer
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Triplets
@app.get("/triplets", response_model=TripletResponse)
async def get_triplets(graph_id: str = "default"):
    if not await check_in_cache(graph_id):
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
    if not await check_in_cache(graph_id):
        raise HTTPException(status_code=404, detail="Graph ID not found.")

    try:
        graph = await run_in_thread(graphs[graph_id].get_graph_json)
        nodes = [Node(**node) for node in graph['nodes']]
        edges = [Edge(**edge) for edge in graph['edges']]  # This ensures `label` is enforced

        return GraphResponse(nodes=graph['nodes'], edges=graph['edges'])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload", response_model=UploadResponse)
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

        if not await check_in_cache(graph_id):
            pipeline = await run_in_thread(build_pipeline_and_graph, graph_id, contents)
            graphs[graph_id] = pipeline
        else:
            pipeline = graphs[graph_id]
            await run_in_thread(pipeline.update_index, contents)

        # Ensure the graph is built and updated

        graph= await get_graph(graph_id)

        return UploadResponse(
            graph= graph,
            graph_id=graph_id
        )
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
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
