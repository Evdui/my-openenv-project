---
title: my-openenv-project
emoji: 📧
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
tags:
  - openenv
short_description: Email classification OpenEnv environment
---

# Email Classification Environment

An OpenEnv-compatible reinforcement learning environment where an AI agent learns to classify emails into the correct category. This simulates a real-world task that operations teams, customer support agents, and personal assistants perform daily.

## Motivation

Email overload is a genuine productivity problem. Training an RL agent to accurately triage emails — distinguishing urgent messages from spam and routine replies — has direct applications in AI-powered email clients, customer support automation, and enterprise inbox management tools.

## Environment Overview

The agent receives an email and must classify it into one of three actions:
- `mark_important` — for urgent emails requiring immediate attention
- `mark_spam` — for unsolicited or promotional emails
- `reply` — for emails that need a thoughtful response

## Action Space

| Action | Description |
|---|---|
| `mark_important` | Mark the email as urgent/important |
| `mark_spam` | Move the email to spam |
| `reply` | Flag the email as requiring a reply |

## Observation Space

| Field | Type | Description |
|---|---|---|
| `email` | string | The email content the agent must classify |
| `task_id` | string | The current task identifier (easy/medium/hard) |

## Tasks

| Task | Difficulty | Description |
|---|---|---|
| `easy` | Easy | Classify an obviously urgent email ("Urgent: Meeting at 5 PM") |
| `medium` | Medium | Classify a clear spam email ("Win a free iPhone!!! Click now!!!") |
| `hard` | Hard | Classify an ambiguous email requiring a reply ("Can you review this document by tomorrow?") |

Tasks increase in difficulty as the email content becomes less obviously categorizable, requiring better language understanding from the agent.

## Reward Function

| Outcome | Reward |
|---|---|
| Correct classification | 0.9 |
| Partially correct (mark_important on non-spam) | 0.5 |
| Incorrect classification | 0.1 |

Rewards are strictly between 0.0 and 1.0, providing a meaningful signal for RL training. The reward function never returns 0 or 1 exactly, ensuring stable gradient signals.

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/reset` | POST | Start a new episode with a given task_id |
| `/step` | POST | Submit an action and receive reward |
| `/state` | GET | Get current environment state |
| `/tasks` | GET | List all available tasks with graders |
| `/grader` | POST | Grade a result directly |
| `/health` | GET | Health check |

## Setup and Usage

### Local Development

```bash
pip install -r requirements.txt
uvicorn server.app:app --host 0.0.0.0 --port 7860
```

### Docker

```bash
docker build -t email-classification-env .
docker run -p 7860:7860 email-classification-env
```

### OpenEnv Validation

```bash
pip install openenv-core
openenv validate --verbose
```

## Baseline Inference

The baseline inference script uses an LLM to classify emails and logs results in the required OpenEnv format.

```bash
# With LLM
API_BASE_URL=<your-endpoint> MODEL_NAME=<your-model> HF_TOKEN=<your-token> python inference.py

# Without LLM (fallback to rule-based)
python inference.py
```

### Baseline Scores

| Task | Score |
|---|---|
| easy | ~0.90 |
| medium | ~0.90 |
| hard | ~0.90 |

## Project Structure

```
├── app/
│   ├── __init__.py
│   └── graders.py        # Task grader functions
├── server/
│   ├── __init__.py
│   ├── app.py            # FastAPI server
│   └── environment.py    # Email environment logic
├── Dockerfile
├── inference.py          # Baseline inference script
├── openenv.yaml          # OpenEnv manifest
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `API_BASE_URL` | Optional | LLM API endpoint |
| `MODEL_NAME` | Optional | LLM model identifier |
| `HF_TOKEN` | Optional | Hugging Face API key |