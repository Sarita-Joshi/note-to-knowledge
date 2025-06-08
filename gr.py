import gradio as gr
from pyvis.network import Network
import webbrowser
import os
from graph_visualizer import build_and_open_graph
from rag_pipeline import RagPipeline

app = RagPipeline()

# Color settings for entity types
type_colors = {
    "Person": "#FF6961",
    "Scientific Theory": "#779ECB",
    "Concept": "#77DD77",
    "Location": "#FFD700",
    "Organization": "#FFB347",
    "Unknown": "#D3D3D3"
}


# Gradio Interface
graph_html =  build_and_open_graph([])

# iframe_html = f"""
# <iframe src="graph.html" width="100%" height="750px" frameborder="0"></iframe>
# """

demo = gr.Interface(
    fn=app.query,
    inputs=gr.Textbox(lines=2, placeholder="Ask a question about the document..."),
    outputs="text",
    title="GraphRAG Assistant",
    description="Ask questions and explore the knowledge graph extracted from your document."
)

# Add HTML viewer
with gr.Blocks() as app:
    gr.Markdown("## 🧠 Knowledge GraphRAG App")
    gr.HTML(graph_html)
    demo.render()

app.launch()
