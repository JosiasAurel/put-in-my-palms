from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess
from dotenv import load_dotenv
import os
import uvicorn
from contextlib import asynccontextmanager
import redis

# load environment variables
load_dotenv()

ROOT_DOMAIN = os.getenv("ROOT_DOMAIN")
APP_PORT = int(os.getenv("APP_PORT", 8000))
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

redis_client = redis.Redis(port=REDIS_PORT, db=REDIS_DB)



LAST_PORT = 8080

# we're assigning ports in increments of 1 starting from 8080
def assign_port() -> int:
    global LAST_PORT
    LAST_PORT += 1
    return LAST_PORT

# project store has the form
# ProjectName:[ProjectPort, ChildProcess]
projects_store = {}

# this function will regenerate the caddy config based on the newly added proejct paths and their ports
def regenerate_caddy_config() -> None:
    caddy_config = f"""
        {ROOT_DOMAIN} {{
            handle {{
                reverse_proxy localhost:{APP_PORT}
            }}
        }}
    """

    for project_name, project_info in projects_store.items():
        project_caddy_config = f"""
        {project_name}.{ROOT_DOMAIN} {{
            handle {{
                reverse_proxy localhost:{project_info[0]}
                header {{
                    -X-Frame-Options
                    Content-Security-Policy "frame-ancestors *"
                    Access-Control-Allow-Origin "*"
                    Access-Control-Allow-Methods "GET, POST, OPTIONS, PUT, DELETE"
                    Access-Control-Allow-Headers "Origin, Content-Type, Accept, Authorization"
                    Access-Control-Allow-Credentials false
                    Access-Control-Max-Age 3600
                }}
            }}
        }}
        """

        caddy_config += project_caddy_config

    with open('Caddyfile', "w") as config_f:
        config_f.write(caddy_config)

    # logging the newly generated caddy config soley for debugging purposes
    print(caddy_config)

@asynccontextmanager
async def lifespan(app: FastAPI):
    regenerate_caddy_config()
    yield

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    lifespan=lifespan
)

@app.get("/")
def _index():
    return "Running..."

@app.get("/projects/{project_name}")
def _run_app(project_name: str):
    if not is_urlsafe(project_name):
        return { "success": False }
    project_port = 0
    # if project is already running, just return on which port the project is running
    if project_name in projects_store.keys():
        project_ps = projects_store[project_name][1]
        # if the project has not terminated, tell the user it is still running
        if project_ps.poll() is None:
            return { "success": True, "port": projects_store[project_name][0], "url": f"{project_name}.{ROOT_DOMAIN}" }
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
    return { "success": True, "port": project_port, "url": f"{project_name}.{ROOT_DOMAIN}" }

def is_urlsafe(name: str) -> bool:
    return all([
        not name.startswith("-"),
        not name.endswith("-"),
        "_" not in name,
        "!" not in name,
        " " not in name,
        "@" not in name,
        ".." not in name,
        "#" not in name
    ])


if __name__ == "__main__":
    uvicorn.run("expose:app", host="0.0.0.0", port=APP_PORT, reload=True)
