from fastapi.testclient import TestClient

from meta_loop.test_machine.app import app

client = TestClient(app)


def test_upload_code():
    files = {"files": ("test_file.py", b'print("Hello, World!")')}
    response = client.post("/upload/", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "agent_id" in data
    assert "info" in data
    assert len(data["info"]) == 1
    assert data["info"][0]["filename"] == "test_file.py"


def test_execute_code():
    # First, upload a file
    files = {"files": ("test_file.py", b'print("Hello, World!")')}
    upload_response = client.post("/upload/", files=files)
    data = upload_response.json()
    agent_id = data["agent_id"]

    # Then, execute the uploaded file
    response = client.post(f"/execute/?agent_id={agent_id}&filename=test_file.py")
    assert response.status_code == 200
    data = response.json()
    assert "stdout" in data
    assert data["stdout"] == "Hello, World!\n"


def test_run_tests():
    # First, upload a test file
    files = {"files": ("test_file.py", b"def test_example():\n    assert True")}
    upload_response = client.post("/upload/", files=files)
    data = upload_response.json()
    agent_id = data["agent_id"]

    # Then, run tests in the uploaded directory
    response = client.post(f"/test/?agent_id={agent_id}")
    assert response.status_code == 200
    data = response.json()
    assert "stdout" in data
    assert "1 passed" in data["stdout"]
