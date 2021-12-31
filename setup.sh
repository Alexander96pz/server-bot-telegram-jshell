docker build -t base -f dockerfiles/base-dockerfile .
docker build -t java -f dockerfiles/java-dockerfile .
docker build -t java-repl -f dockerfiles/java-repl-dockerfile .
docker build -t main -f dockerfiles/main-dockerfile .
docker run -v /var/run/docker.sock:/var/run/docker.sock main:latest
