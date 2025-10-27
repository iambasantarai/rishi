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
        contents=input,
    )

    return response.text

def get_pr_diff(repo_name: str, pr_number: int)-> str:
    github_pat = os.environ.get("GITHUB_PAT")
    github_username = os.environ.get("GITHUB_USERNAME")
    headers = {
        "Authorization": f"Bearer {github_pat}",
        "Accept": "application/vnd.github.v3.diff"
    }
    url = f"https://api.github.com/repos/{github_username}/{repo_name}/pulls/{pr_number}"

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"ERROR: {response.text}")
        return

    return response.text

def review_code_with_llm(diff: str, pr_title: str) -> str:
    prompt = f"""Review this pull request and provide constructive feedback.
    PR Title: {pr_title}

    Code Diff:
    {diff}

    Provide a concise review focusing on:
    1. Potential bugs or issues
    2. Code quality and best practices
    3. Security concerns
    4. Performance considerations

    Keep your review practical and actionable."""

    response = google_genai_client(prompt)
    return response

diff = get_pr_diff("rishi", 1)
if not diff:
    print("failed to get diff")
review = review_code_with_llm(diff, "Read pr diff from repository")

print(review)

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
