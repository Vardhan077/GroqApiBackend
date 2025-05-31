from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
from dotenv import load_dotenv
from pydantic import BaseModel
import os

load_dotenv()

print("GROQ key:", os.getenv("GROQ_API_KEY"))

os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

agent = Agent(
    model=Groq("llama3-8b-8192"),  # use a safe default model
    description="You are an insurance agent who suggests trending plans based on age.",
    tools=[DuckDuckGoTools()],
    markdown=True,
)

app = FastAPI()

# Add CORS middleware here
origins = [
    "*"  # your frontend origin
    # You can add more origins or use ["*"] for testing but not recommended for production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # or ["*"] to allow all origins
    allow_credentials=True,
    allow_methods=["*"],            # allow all HTTP methods
    allow_headers=["*"],            # allow all headers
)


class UserRequest(BaseModel):
    query: str

@app.get("/")
def root():
    return {"message": "Server running"}


# @app.post("/ask")
# def ask_question(user_input: UserRequest):
#     try:
#         response = agent.run(user_input.query)
#         print("Agent response:", response)
#         return {"response": response.content}
#     except Exception as e:
#         print("Exception:", e)
#         return {"error": str(e)}


from fastapi.responses import StreamingResponse

@app.post("/ask")
async def ask_question(user_input: UserRequest):
    async def event_stream():
        
        try:
            response = agent.run(user_input.query)
            for chunk in response.content.split():
                yield f"{chunk} "  # Send words as individual chunks
                
        except Exception as e:
            yield f"Error: {str(e)}"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
