from fastapi import FastAPI
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
from dotenv import load_dotenv
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

@app.get("/")
def root():
    return {"message": "Server running"}

@app.post("/ask")
def ask_question():
    try:
        response = agent.run("Suggest me some trending insurance plans for a 25-year-old")
        print("Agent response:", response)
        return {"response": response.content}
    except Exception as e:
        print("Exception:", e)
        return {"error": str(e)}
