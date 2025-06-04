from fastapi import FastAPI
import subprocess

app = FastAPI()

LAST_PORT = 8080

# we're assigning ports in increments of 1 starting from 8080
def assign_port() -> int:
    global LAST_PORT
    LAST_PORT += 1
    return LAST_PORT

# project store has the form
# ProjectName:[ProjectPort, ChildProcess]
projects_store = {}

@app.get("/{project_name}")
def _run_app(project_name: str):
    project_port = 0
    # if project is already running, just return on which port the project is running
    if project_name in projects_store.keys():
        project_ps = projects_store[project_name][1]
        # if the project has not terminated, tell the user it is still running
        if project_ps.poll() is None:
            return { "success": True, "port": projects_store[project_name][0] } 
        project_port = projects_store[project_name][0]

    # otherwise, assign a new port to expose the project
    if project_port == 0:
        project_port = assign_port()
    # will reuse the port this project was using before
    
    print("Will be running on port", project_port)
    run_cmd = f"docker run -p {project_port}:8989 jos/palm {project_name}"
    ps = subprocess.Popen(run_cmd.split(" "))
    # print(ps)

    # after the project has been started, add it to the in-memory store
    projects_store[project_name] = [project_port, ps]

    return { "success": True, "port": project_port } 
