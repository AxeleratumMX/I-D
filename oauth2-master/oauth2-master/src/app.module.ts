import { Module } from '@nestjs/common';
import { Oauth2Module } from './oauth2/oauth2.module';
import { TypeOrmModule } from '@nestjs/typeorm';
import { typeOrmConfig } from './config/typeorm.config';

@Module({
  imports: [
    TypeOrmModule.forRoot(typeOrmConfig),
    Oauth2Module,
  ],
})
export class AppModule { }
