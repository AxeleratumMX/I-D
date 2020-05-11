import { TypeOrmModuleOptions } from '@nestjs/typeorm';

export const typeOrmConfig: TypeOrmModuleOptions = {
    type: 'postgres',
    host: process.env.DB_HOST,
    // tslint:disable-next-line: radix
    port: parseInt(process.env.DB_PORT),
    username: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    // database: 'ViliDB',
    database: process.env.DB_NAME,
    schema: 'public',
    entities: [__dirname + '/../**/*.entity.{js,ts}'],
    synchronize: true,
    // namingStrategy: new MyNamingStrategy()


};
