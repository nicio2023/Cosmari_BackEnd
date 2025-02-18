FROM ubuntu:latest
LABEL authors="eloma"

ENTRYPOINT ["top", "-b"]