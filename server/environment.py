class EmailEnv:
    def __init__(self):
        self.tasks = [
            {"id": "easy", "email": "Urgent: Meeting at 5 PM", "correct_action": "mark_important"},
            {"id": "medium", "email": "Win a free iPhone!!! Click now!!!", "correct_action": "mark_spam"},
            {"id": "hard", "email": "Can you review this document by tomorrow?", "correct_action": "reply"}
        ]
        self.current_task = self.tasks[0]

    def reset(self, task_id="easy"):
        for t in self.tasks:
            if t["id"] == task_id:
                self.current_task = t
                break
        return {"email": self.current_task["email"], "task_id": self.current_task["id"]}

    def step(self, action):
        correct = self.current_task["correct_action"]
        if action == correct:
            reward = 0.9
        elif action == "mark_important":
            reward = 0.5
        else:
            reward = 0.1
        return {"email": self.current_task["email"], "task_id": self.current_task["id"]}, reward, True, {}

    def state(self):
        return {"email": self.current_task["email"], "task_id": self.current_task["id"]}