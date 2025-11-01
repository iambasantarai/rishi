<h2 align="center">rishi</h2>
<p align="center">an experimental LLM powered PR reviewer</p>

### Overview

While exploring open-source projects, i often noticed that pull requests were being reviewed by CodeRabbit, leaving well-crafted and insightful comments.
That instantly sparked my curiosity, how does it actually work?

I started reverse-engineering the idea and had a few back-and-forth conversations with Claude, which helped me piece together its underlying workflow and structure.

Fueled by curiosity, I decided to build my own experimental version and that's how this project came to life.

Here's how it works:
- Receives a webhook from GitHub when a pull request is opened, reopened or updated
- Fetches the code diff from the PR
- Sends the diffs & commits to an LLM for review and feedback generation
- Posts the comments back to the PR

### Getting started

- Get the repository
    ```sh
    git clone https://github.com/iambasantarai/rishi.git && cd rishi
    ```

- Get your api keys
    - GitHub Token: 
        - Go to GitHub Settings → Developer settings → Personal access tokens → Generate new token
        - Create classic or fine grained token
            - Classic
                - Select scopes: `repo`(full control)
            - Fine grained tokens
                - Permissions: `Pull requests` with `Access: Read and write`
    - Google AI Studio API Key: Get from `https://aistudio.google.com`

- Configure environment variables
    ```sh
    cp .env.example .env
    ```

- Install dependencies
    ```sh
    uv sync
    ```

- Start server
    ```sh
    uv run fastapi dev main.py
    ```

- Host it or expose it with ngrok
    ```sh
    ngrok http 8000
    ```
    You'll get a URL like `https://example-url.ngrok-free.dev -> http://localhost:8000`

- Configure GitHub webhook:
    - Go to your test repo → Settings → Webhooks → Add webhook
    - Payload URL: `https://example-url.ngrok-free.dev/webhook`
    - Content type: `application/json`
    - Select: "Let me select individual events" → Check only "Pull requests"

> I've only tested it with gemini, hopefully openai works as well.

### Test It!

- Create a test branch in your repo
- Make some changes (add a file, modify code)
- Open a pull request
- Watch your terminal - you'll see the webhook hit
- Check the PR - you'll see the review comment!
