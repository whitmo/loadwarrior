from locust import Locust, task

class ATest(Locust):
    @task
    def index(l):
        l.client.get("/")
