import { Module, HttpModule } from '@nestjs/common';
import { QueuingModule } from './queuing/queuing.module';

@Module({
  imports: [
    QueuingModule,
  ],
  controllers: [],
  providers: [],
})
export class AppModule { }
