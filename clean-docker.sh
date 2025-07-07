# stop all containers
docker stop $(docker ps -q)

# remove all containers. stopped or not
docker rm $(docker ps -aq)

# remove all docker images
docker rmi -f $(docker images -q)

# cleanup dangling volumes and network
docker volume prune -f
docker network prune -f
