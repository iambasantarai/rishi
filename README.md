<h2 align="center">rishi</h2>
<p align="center">an experimental LLM powered PR reviewer</p>

### Overview

This is a reverse-engineered version of CodeRabbit, designed as an experimental PR reviewer powered by a language model.

Here's how it works:
- Receives a webhook from GitHub when a pull request is opened, reopened or updated
- Fetches the code diff from the PR
- Sends the diffs & commits to an LLM for review and feedback generation
- Posts the comments back to the PR
