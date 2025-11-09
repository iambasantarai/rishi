<h2 align="center">rishi</h2>
<p align="center">i'm assuming this is how code rabbit works?</p>

#### Here's how it works:

- Receives a webhook from GitHub when a pull request is opened, reopened or updated
- Fetches the code diffs and commits from the PR
- Sends the diffs & commits to an LLM for review and feedback generation
- Posts the comments back to the PR

[Getting Started](https://github.com/iambasantarai/rishi/blob/main/USAGE.md)
