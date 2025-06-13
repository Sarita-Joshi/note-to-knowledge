from llama_index.llms.gemini import Gemini
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index_server.config import (
    GEMINI_API_KEY,
    GROQ_API_KEY,
)

llm = Gemini(api_key=GEMINI_API_KEY, model="gemini-1.5-flash")  # or "gemini-pro", etc.

# from llama_index.llms.groq import Groq
# llm = Groq(api_key=GROQ_API_KEY, model="llama3-70b-8192")  # or "llama-3-70b-8192", etc.

# ---- Use OPenai ----
llm = OpenAI(model="gpt-3.5-turbo")  # You can use  for lower cost
embed_model = OpenAIEmbedding(model="text-embedding-3-small")
