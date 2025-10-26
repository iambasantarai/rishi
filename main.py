import os
import time
import pprint
import requests
from fastapi import FastAPI, APIRouter, status
from openai import OpenAI
from dotenv import load_dotenv
from google import genai
from google.genai import types

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

INSTRUCTION="You are a pull request reviewer that talks like a pirate."

pp = pprint.PrettyPrinter(indent=2)

def openai_client(input: str):
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    response = client.responses.create(
        model="gpt-4o",
        instructions=INSTRUCTION,
        input=input,
    )

    return response.output_text

def google_genai_client(input: str):
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY")
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=INSTRUCTION
        ),
        contents="Explain how AI works in a few words",
    )

    return response.text

def get_pr_details(repo_name: str, pr_number: int):
    print(">>> fetching pr details")
    headers = {
        "Accept": "application/vnd.github.v3.diff"
    }
    url = f"https://api.github.com/repos/derailed/{repo_name}/pulls/{pr_number}/commits"
    response = requests.get(url, headers)
    pp.pprint(response.json())

get_pr_details("k9s", 3640)

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
    Sends a request to the LLM and returns a response.
    """
    response = ""
    match os.environ.get("LLM_PROVIDER"):
        case "google":
            print("calling google")
            response = google_genai_client(question)
        case "openai":
            print("calling openai")
            response = openai_client(question)
        case _:
            print("Invalid llm provider.")
            return

    return {"answer": response}

app.include_router(router)
