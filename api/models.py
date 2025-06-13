from pydantic import BaseModel
from typing import List, Dict, Optional

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
    relationship: str
    description: Optional[str]

class GraphResponse(BaseModel):
    nodes: List[Node]
    edges: List[Edge]

class UploadResponse(BaseModel):
    graph: GraphResponse
    graph_id: str