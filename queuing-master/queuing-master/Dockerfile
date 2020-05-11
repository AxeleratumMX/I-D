# IMPORTANT: RUN THIS FILE FROM GIT ROOT ANd SEND THIS FILE AS PARAMETER!

FROM alpine:3.10 AS stage1

WORKDIR /workspace

# Copy files from local to docker image
COPY ["./dist/", "./dist/"]
COPY ["./package.json", "./"]
COPY ["./package-lock.json", "./"]

RUN apk add --update nodejs npm python make g++ \
    && npm install --production 



FROM alpine:3.10 AS stage2

WORKDIR /workspace

# Identify the maintainer of the image
LABEL maintainer="uriel@axeleratum.com"

# Copy files from local to docker image
COPY --from=stage1 /workspace/ /workspace/

RUN apk add --update nodejs npm

# Initial command
CMD npm run start:prod
