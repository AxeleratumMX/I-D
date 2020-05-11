## login as sudo
sudo su

## install curl
apt install curl

## install nodejs
curl -sL https://deb.nodesource.com/setup_12.x | bash -
apt-get install -y nodejs

## install nestjs cli
npm install -g @nestjs/cli

## create new project
nest new project_name

## open vscode in the project folder
code project_name/

## remove these files
app.controller.ts
app.controller.spec.ts
app.service.ts

## remove the the references in app.module/ts

## install library to create uuid and add it to the project
npm install --save uuid
npm add uuid

## run  server in dev mode
npm run start:dev

## install class-validator and class-transform and add it to the project
npm install class-validator class-transformer --save
npm add class-validator class-transformer --save

## Install scheduler
npm i --save nest-schedule
