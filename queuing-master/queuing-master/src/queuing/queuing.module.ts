import { Module, HttpModule } from '@nestjs/common';
import { QueuingController } from './queuing.controller';
import { ScheduleModule } from 'nest-schedule';
import { ScheduleService } from './schedule.service';
import { FilterDto } from './dto/filter.dto';
import { QueuingService } from './queuing.service';

@Module({
  imports: [
    HttpModule,
    ScheduleModule.register({}),
  ],
  controllers: [QueuingController],
  providers: [ScheduleService, QueuingService],
  exports: []
})
export class QueuingModule { }

// declare global {
//   const queue: FilterDto[];
// }
