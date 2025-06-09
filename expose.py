from fastapi import FastAPI
import subprocess
from dotenv import config
import os

# load environment variables
config()

ROOT_DOMAIN = os.getenv("ROOT_DOMAIN")

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

@app.get("/")
def _index():
    return "Running..."

@app.get("/projects/{project_name}")
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
    print("running command")
    print(run_cmd)
    # print(ps)

    # after the project has been started, add it to the in-memory store
    projects_store[project_name] = [project_port, ps]


    # regenerate caddy config such that it includes the newly added proejct
    regenerate_caddy_config()
    return { "success": True, "port": project_port } 

# this function will regenerate the caddy config based on the newly added proejct paths and their ports
def regenerate_caddy_config() -> None:
    caddy_config = f"""
        {ROOT_DOMAIN} {{
            handle {{
                respond "TerminalCraft Project Demo"
            }}
        }}
    """

    for project_name, project_info in projects_store.items():
        project_caddy_config = f"""
        {project_name}.{ROOT_DOMAIN} {{
            reverse_proxy localhost:{project_info[0]}
        }}
        """

        caddy_config += project_caddy_config

    with open('Caddyfile', "w") as config_f:
        config_f.write(caddy_config)

    # logging the newly generated caddy config soley for debugging purposes
    print(caddy_config)
