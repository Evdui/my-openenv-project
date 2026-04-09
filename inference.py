import os
from openai import OpenAI
import json
import urllib.request

# ENV VARIABLES
LLM_BASE_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

# YOUR ENV API
ENV_BASE_URL = "https://evdui-my-openenv-project.hf.space"

BENCHMARK = "my-openenv-project"
MAX_STEPS = 5

client = None
if API_KEY and LLM_BASE_URL:
    client = OpenAI(
        api_key=API_KEY,
        base_url=LLM_BASE_URL
    )


def post_request(url, data=None):
    try:
        if data:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode(),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
        else:
            req = urllib.request.Request(url, method="POST")

        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())

    except Exception as e:
        print(f"[ERROR] API call failed: {e}")
        return None


def fallback_action(email):
    email = email.lower()
    if "urgent" in email or "meeting" in email:
        return "mark_important"
    elif "free" in email or "win" in email or "click" in email:
        return "mark_spam"
    else:
        return "reply"


def get_action_from_llm(email):
    if client is None:
        return fallback_action(email)

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You classify emails into exactly one of: mark_important, mark_spam, reply. Reply with only the action, nothing else."},
                {"role": "user", "content": email}
            ],
            temperature=0.2
        )

        action = response.choices[0].message.content.strip().lower()

        if action not in ["mark_important", "mark_spam", "reply"]:
            return fallback_action(email)

        return action

    except Exception as e:
        print(f"[ERROR] LLM call failed: {e}")
        return fallback_action(email)


def run_episode(task_id="easy"):
    print(f"[START] task={task_id} env={BENCHMARK} model={MODEL_NAME}")

    rewards = []
    success = False
    step = 0

    state = post_request(f"{ENV_BASE_URL}/reset", {"task_id": task_id})

    if state is None:
        print(f"[END] success=false steps=0 score=0.0001 rewards=")
        return

    for step in range(1, MAX_STEPS + 1):
        email = state.get("email", "")
        action = get_action_from_llm(email)

        data = post_request(f"{ENV_BASE_URL}/step", {"action": action, "task_id": task_id})

        if data is None:
            print(f"[END] success=false steps={step} score=0.0001 rewards=")
            return

        reward = float(data.get("reward", 0.0))
        done = data.get("done", False)
        state = data.get("observation", {})

        print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error=null")
        rewards.append(reward)

        if done:
            success = reward > 0
            break

    score = sum(rewards) / len(rewards) if rewards else 0.0
    score = max(1e-6, min(score, 1 - 1e-6))
    rewards_str = ",".join([f"{r:.2f}" for r in rewards])
    print(f"[END] success={str(success).lower()} steps={step} score={score:.4f} rewards={rewards_str}")


if __name__ == "__main__":
    for task in ["easy", "medium", "hard"]:
        run_episode(task)