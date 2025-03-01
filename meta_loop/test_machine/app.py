import os
import subprocess
import tempfile
from typing import List
from fastapi import FastAPI, File, UploadFile
from collections import defaultdict
from uuid import uuid4

app = FastAPI()

agent_to_files = defaultdict(str)


@app.post("/upload/")
async def upload_code(files: List[UploadFile] = File(...)):
    agent_id = f"agent_{uuid4()}"
    temp_dir = tempfile.mkdtemp(prefix=f"agent_{agent_id}_")
    file_infos = []
    for file in files:
        file_location = os.path.join(temp_dir, file.filename)
        with open(file_location, "wb") as f:
            f.write(await file.read())
        file_infos.append({"filename": file.filename, "location": file_location})
    agent_to_files[agent_id] = temp_dir
    return {"agent_id": agent_id, "info": file_infos}


@app.post("/execute/")
async def execute_code(agent_id: str, filename: str):
    directory = agent_to_files[agent_id]
    file_location = os.path.join(directory, filename)
    if os.path.exists(file_location):
        result = subprocess.run(
            ["python", file_location], capture_output=True, text=True
        )
        return {"stdout": result.stdout, "stderr": result.stderr}
    return {"error": "File not found"}


@app.post("/test/")
async def run_tests(agent_id: str):
    directory = agent_to_files[agent_id]
    if os.path.exists(directory):
        result = subprocess.run(["pytest", directory], capture_output=True, text=True)
        return {"stdout": result.stdout, "stderr": result.stderr}
    return {"error": "Test directory not found"}
