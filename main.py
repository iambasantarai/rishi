import os
import time
from fastapi import FastAPI, APIRouter, status
from openai import OpenAI
from dotenv import load_dotenv

tags_metadata = [
    {
        "name": "heartbeat",
        "description": "Heartbeat of a server",
    },
    {
        "name": "ask",
        "description": "OpenAI will answer you.",
    },
]

app = FastAPI(
    title="Rishi",
    version="0.0.1",
    openapi_tags=tags_metadata
)
router = APIRouter()

# Load envornment variables
load_dotenv()

@router.get("/heartbeat", status_code=status.HTTP_200_OK, tags=["heartbeat"])
def heartbeat():
    """
    Returns a server heartbeat timestamp in nanoseconds.
    """
    heartbeat = time.monotonic_ns()
    return {"heartbeat": heartbeat}

@router.post("/ask", status_code=status.HTTP_200_OK, tags=["ask"])
def ask(question: str):
    """
    Sends a request to the OpenAI API and returns a response.
    """
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    response = client.responses.create(
        model="gpt-4o",
        instructions="You are a pull request reviewer that talks like a pirate.",
        input=question,
    )
    return {"answer": response.output_text}

app.include_router(router)
