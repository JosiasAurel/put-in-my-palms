from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import uvicorn
from contextlib import asynccontextmanager
import docker
import random
import socket

# load environment variables
load_dotenv()

ROOT_DOMAIN = os.getenv("ROOT_DOMAIN")
APP_PORT = int(os.getenv("APP_PORT", 8000))

docker_client = docker.from_env()

def get_palms_containers():
    palms_containers = list(filter(lambda container: "palms-" in container, docker_client.containers.list()))
    return palms_containers

def get_container_port(container) -> int:
    return int(container.attrs["HostConfig"]["PortBindings"]["8989/tcp"][0]["HostPort"])

def is_port_in_use(port, host="127.0.0.1"):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        result = s.connect_ex((host, port))
        return result == 0

# naive approach to selecting another port to use
def suggest_container_port():
    used_ports = list(map(lambda container: get_container_port(container), docker_client.containers.list()))
    if len(used_ports) == 0:
        suggested_port = 0
        while True:
            suggested_port = random.randint(APP_PORT + 1, 9999)
            if not is_port_in_use(suggested_port): break
        return suggested_port
    # it should be able to pick a port that is not yet used on the machine
    return max(used_ports) + 1

# this function will regenerate the caddy config based on the newly added proejct paths and their ports
def regenerate_caddy_config() -> None:
    caddy_config = f"""
        {ROOT_DOMAIN} {{
            handle {{
                reverse_proxy localhost:{APP_PORT}
            }}
        }}
    """

    for container in get_palms_containers():
        container_port = get_container_port(container)
        project_name = container.name.split("-")[1]
        project_caddy_config = f"""
            {project_name}.{ROOT_DOMAIN} {{
                handle {{
                    reverse_proxy localhost:{container_port}
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

    with open("Caddyfile", "w") as config_f:
        config_f.write(caddy_config)

@asynccontextmanager
async def lifespan(app: FastAPI):
    regenerate_caddy_config()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
)

@app.get("/")
def _index():
    return "Running..."

@app.get("/projects/{project_name}")
def _run_app(project_name: str):
    if not is_urlsafe(project_name):
        return { "success": False }

    try:
        docker_client.containers.get("palms-" + project_name) 
    except docker.errors.NotFound:
        container_port = suggest_container_port()
        docker_client.containers.run("jos/palm", name="palms-" + project_name, ports={"8989/tcp": container_port }, command=project_name, detach=True)

    regenerate_caddy_config()

    return { "success": True, "url": f"{project_name}.{ROOT_DOMAIN}" }

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
