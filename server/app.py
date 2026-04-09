from fastapi import FastAPI
from pydantic import BaseModel
from server.environment import EmailEnv

app = FastAPI()
env = EmailEnv()

class ActionInput(BaseModel):
    action: str
    task_id: str = "easy"

@app.post("/reset")
def reset(data: dict = {}):
    task_id = data.get("task_id", "easy") if data else "easy"
    return env.reset(task_id)

@app.post("/step")
def step(data: ActionInput):
    obs, reward, done, info = env.step(data.action)
    return {"observation": obs, "reward": reward, "done": done, "info": info}

@app.get("/state")
def state():
    return env.state()

@app.get("/tasks")
def get_tasks():
    return [
        {"id": "easy", "grader": "app.graders:GradeEasy"},
        {"id": "medium", "grader": "app.graders:GradeMedium"},
        {"id": "hard", "grader": "app.graders:GradeHard"}
    ]

@app.post("/grader")
def grader(data: dict):
    reward = data.get("reward", 0.0)
    return {"score": max(1e-6, min(float(reward), 1 - 1e-6))}

@app.get("/health")
def health():
    return {"status": "healthy"}