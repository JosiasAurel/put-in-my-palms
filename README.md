# TerminalCraft Review Container

This will be a container that will make it easier to run and review terminalcraft programs. 

How this is going to work

- A linux container
- All the languages that I expect Hack Clubbers to use to develop their TerminalCraft projects in
    - Ruby, Python, C/C++, Rust, JavaScript/Node.js, Java, C# (dotnet), Lua 5.4, LuaJIT
- The container is going to take as argument 
    - full url to project it has to clone from PR or folder in the terminalcraft repository
        - could even be just the branch name it has to checkout out to and commit hash/HEAD
- The process
    - Initialize the linux Docker container
    - Clone the repository 
    - Changes directory into the project
    - Binds to an exposed port on the host machine
    - Returns a url one can visit to run the terminalcraft program
        - *If possible, the readme of the terminalcraft program will be printed 
    - Exiting the container clears it's memory
- Containers should be cleaned up after a day of inactivity

## Setting up

### Requirements
- Docker
- Python3 
- caddy-server 

### Getting it to run
1. Install the dependencies with 
```shell
pip3 install -r requirements.txt --break-system-packages
```
2. Build the Docker image
```shell
docker build -t jos/palm .
```
3. Set environment variables
Replace `ROOT_DOMAIN` with the root domain you want to use and `APP_PORT`.
- Set A record `terminalcraft.josiasw.dev` that points to the IP of your service
- Set an A record that points to the IP of your server. e.g A | `*.terminalcraft.josiasw.dev` 192.168.2.111
```
ROOT_DOMAIN=terminalcraft.josiasw.dev
APP_PORT=8001
```
3. Start the server using
```shell
python3 expose.py
```
4. Start caddy server in watch mode
```shell 
caddy run --watch
```

## Usage
```
GET terminalcraft.josiasw.dev/projects/<project-name>
^ This will start a new Docker container and expose to the internet under <project-name>.terminalcraft.josiasw.dev (or whatever <project-name>.your-subdomain.tld)
```

```
Navigating to <project-name>.your-subdomain.tld will start a session and connect to that Docker container for your usage
```

## Configuring an app for this

Create a `config.json` in the root of the project folder with the following structure
```json
{
    "setup": "single command to setup the project and install dependencies",
    "run": "command to run the project"
}
```
