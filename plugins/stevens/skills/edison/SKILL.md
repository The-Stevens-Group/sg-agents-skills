---
name: edison
description: Conduct scientific research using Edison's autonomous literature search API. Use when the user asks to research a scientific question, find papers, or review literature on a topic. Edison searches hundreds of papers and returns a cited answer.
argument-hint: <research question>
user-invocable: true
---

# Edison Research

You are delegating a scientific literature search to the Edison API. Edison is an autonomous research agent that searches hundreds of papers and synthesizes a cited answer. Your job is to submit the query, wait for the result, and report it.

## CRITICAL: Do NOT search for the answer yourself

> **Edison takes 1–5 minutes to respond. This is normal. BE PATIENT.**
>
> While waiting for Edison, you MUST NOT:
> - Search the web, PubMed, bioRxiv, or any other source
> - Attempt to answer the research question from your own knowledge
> - Use any other tool to find papers or literature
> - Speculate about what the answer might be
>
> Edison's search is comprehensive (hundreds of papers with full-text analysis). Anything you find on your own would be redundant and inferior. Your role is to **submit and wait**, not to compete with Edison.
>
> The ONLY thing you may do while an Edison query is running is launch additional Edison queries if the user asked for multiple.

## Input

<query>
$ARGUMENTS
</query>

If no query is provided, ask the user what they want to research.

## Step 1: Run the query

Resolve `scripts/edison_query.sh` relative to the installed directory of this skill (the same directory as this file), never through a different plugin's cache. Use the host's asynchronous execution mechanism when available, and give progress updates during the wait.

```bash
"<installed-skill-directory>/scripts/edison_query.sh" --query "<research question>" --max-wait 540
```

The script authenticates, submits the query, and polls every 15s until Edison returns an answer. Progress messages appear on stderr. The final result is a JSON object on stdout:

```json
{
  "task_id": "uuid",
  "status": "success",
  "formatted_answer": "The full cited answer in markdown",
  "answer": "Plain text answer",
  "has_successful_answer": true
}
```

If the local wait limit is reached before Edison finishes, the task is still running on Edison's servers. The script returns a resumable, non-fatal JSON object:

```json
{
  "task_id": "uuid",
  "status": "running",
  "recoverable": true,
  "has_successful_answer": false,
  "resume_command": "/path/to/edison_query.sh --task-id uuid"
}
```

In this case, do **not** answer from memory or search other sources. Poll the same task id again:

```bash
"$EDISON_SCRIPT" --task-id <task_id> --max-wait 540
```

Repeat polling until `status` is `success` or Edison returns a terminal failure. If the shell tool itself times out but the last visible output contains a `task_id`, recover using `--task-id <task_id>`.

If the script outputs an `error` field, report the error to the user and stop.

**API key not set:** If the error indicates `EDISON_PLATFORM_API_KEY not set`, ask the user to configure their Edison API key through the host’s secret-input mechanism or their local environment; never request a key in chat. Tell them they can get one from [platform.edisonscientific.com/profile](https://platform.edisonscientific.com/profile) and set it in their agent environment. Claude Code users can put it in `~/.claude/settings.json` under `"env"`; Codex users can export it in their shell or project environment. Do NOT proceed with any other action — wait for the user to provide the key.

### Running multiple queries

If the user asks multiple research questions, launch each as a separate background Bash call. Wait for all to complete before reporting.

## Step 2: Report the answer

Once the script returns:

1. Report `formatted_answer` to the user verbatim — it contains inline citations and is the primary output.
2. Note the `task_id` — the user may want it for follow-up queries.
3. If `has_successful_answer` is `false`, tell the user Edison could not confidently answer and suggest refining the question.

## Follow-up queries

To continue a previous research thread (e.g., ask a follow-up question that builds on prior context), use `--continue-from`:

```bash
"<installed-skill-directory>/scripts/edison_query.sh" --query "<follow-up question>" --continue-from <task_id> --max-wait 540
```

This reuses the papers and context from the previous task, giving Edison a head start. Use this when the user wants to dig deeper into a topic they already queried.

## Prerequisites

The user must set `EDISON_PLATFORM_API_KEY` in the agent environment. Claude Code users can set it in `~/.claude/settings.json`:

```json
{
  "env": {
    "EDISON_PLATFORM_API_KEY": "your-key-here"
  }
}
```

Keys are available from [platform.edisonscientific.com/profile](https://platform.edisonscientific.com/profile).

`jq` must be installed (`brew install jq` / `apt install jq`).
