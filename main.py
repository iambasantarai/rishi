import os
import time
import pprint
import httpx
from fastapi import FastAPI, APIRouter, status, Request
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
        "name": "webhook",
        "description": "Handle webhook event",
    }
]

app = FastAPI(
    title="Rishi",
    version="0.0.1",
    openapi_tags=tags_metadata
)
router = APIRouter()

# Load envornment variables
load_dotenv()

SYSTEM_PROMPT=f"""
You are rishi - a pull request reviewer who talks like pirate.
You blend serene wisdom with sharp wit, caring deeply about simplicity, readability, maintainability, and architectural coherence.
"""

pp = pprint.PrettyPrinter(indent=2)

def openai_client(input: str):
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    res = client.responses.create(
        model="gpt-4o",
        instructions=SYSTEM_PROMPT,
        input=input,
    )

    return res.output_text

def google_genai_client(input: str):
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY")
    )

    res = client.models.generate_content(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT
        ),
        contents=input,
    )

    return res.text

async def get_pr_diff(repo_name: str, pr_number: int)-> str:
    github_pat = os.environ.get("GITHUB_PAT")
    headers = {
        "Authorization": f"Bearer {github_pat}",
        "Accept": "application/vnd.github.v3.diff"
    }
    url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}"

    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=headers)
        res.raise_for_status()
        return res.text

async def review_code_with_llm(diff: str, pr_title: str):
    prompt = f"""
    Review the following pull request and provide:
    1. A **concise summary** of what this PR does - infer the main changes from the diff and categorize them into features, fixes, fefactors, or other changes.
    2. Present this summary in a **Markdown table** with the following columns:  
       | Type | Description | Files/Sections Affected |
    3. After the table, include **one short paragraph** of practical feedback on code quality, architecture, or maintainability.

    PR Title: {pr_title}

    Code Diff:
    {diff}
    """

    res = ""
    match os.environ.get("LLM_PROVIDER"):
        case "google":
            print(">>> reviewing with google gemini...")
            res = google_genai_client(prompt)
        case "openai":
            print(">>> reviewing with openai...")
            res = openai_client(prompt)
        case _:
            print("Invalid llm provider.")
            return
    return res

async def write_review_comment(repo_name: str, pr_number: int, comment: str):
    github_pat = os.environ.get("GITHUB_PAT")
    headers = {
        "Authorization": f"Bearer {github_pat}",
        "Accept": "application/vnd.github+json"
    }
    url = f"https://api.github.com/repos/{repo_name}/issues/{pr_number}/comments"
    review_comment = {"body": f"## Reviewes from RISHI 🧠\n\n{comment}"}

    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, json=review_comment)
        res.raise_for_status()

@router.get("/heartbeat", status_code=status.HTTP_200_OK, tags=["heartbeat"])
def heartbeat():
    """
    Returns a server heartbeat timestamp in nanoseconds.
    """
    heartbeat = time.monotonic_ns()
    return {"heartbeat": heartbeat}

@router.post("/webhook", status_code=status.HTTP_200_OK, tags=["webhook"])
async def webhook(request: Request):
    payload = await request.json()
    event_type = request.headers.get("X-GitHub-Event")

    if event_type == "pull_request":
        action = payload.get("action")

        if action not in ["opened", "synchronize"]:
            return {"status": "ignored", "reason": f"action '{action}' not relevant"}

        pr = payload["pull_request"]
        pr_number = pr["number"]
        pr_title = pr["title"]
        repo_full_name = payload["repository"]["full_name"]

        diff = await get_pr_diff(repo_full_name, pr_number)
        review_comment = await review_code_with_llm(diff, pr_title)
        await write_review_comment(repo_full_name, pr_number, review_comment)

app.include_router(router)
