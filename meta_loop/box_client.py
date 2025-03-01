import httpx


class Sandbox:
    def __init__(self, base_url: str):
        self.client = httpx.Client(base_url=base_url)
        self.agent_id = None

    def upload_files(self, files: dict):
        response = self.client.post("/upload/", files=files)
        response.raise_for_status()
        data = response.json()
        self.agent_id = data["agent_id"]
        return data

    def execute_code(self, filename: str):
        if not self.agent_id:
            raise ValueError("Agent ID is not set. Please upload files first.")
        response = self.client.post(
            f"/execute/?agent_id={self.agent_id}&filename={filename}"
        )
        response.raise_for_status()
        return response.json()

    def run_tests(self):
        if not self.agent_id:
            raise ValueError("Agent ID is not set. Please upload files first.")
        response = self.client.post(f"/test/?agent_id={self.agent_id}")
        response.raise_for_status()
        return response.json()
