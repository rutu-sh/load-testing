from locust import task, FastHttpUser

class MyUser(FastHttpUser):
    @task
    def my_task(self):
        self.client.get("/")