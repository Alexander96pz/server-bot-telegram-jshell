docker build -t base -f dockerfiles/base-dockerfile .
docker build -t java -f dockerfiles/java-dockerfile .
docker build -t java-repl -f dockerfiles/java-repl-dockerfile .
docker build -t main -f dockerfiles/main-dockerfile .
# docker build -t serversandbox/static .
docker pull alexander96pz/static:latest
docker run --name staticServer -p 8080:8080 alexander96pz/static:latest
#export PRUEBA=$(docker inspect --format '{{ .NetworkSettings.IPAddress }}' staticServer)
docker run -e STATIC_KEY=$(docker inspect --format '{{ .NetworkSettings.IPAddress }}' staticServer) -e API_KEY='1434211966:AAEWS3OWn9W5f4Zb8OqQSrYaeqrBqMn8XFA' -e DB_KEY='u0hzf4t3vypi4gaa:8KoYYAznhQXfnXpR8Kv6@bm1uk41dbgwcar5uvd9e-mysql.services.clever-cloud.com:3306/bm1uk41dbgwcar5uvd9e' -v /var/run/docker.sock:/var/run/docker.sock main:latest