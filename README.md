# TerminalCraft Review Container

This will be a container that will make it easier to run and review terminalcraft programs. 

How this is going to work

- A linux container
- All the languages that I expect Hack Clubbers to use to develop their TerminalCraft projects in
    - Ruby, Python, C/C++, Rust, JavaScript/Node.js, Java, C# (dotnet)
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