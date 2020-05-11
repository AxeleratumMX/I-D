import { Controller, Param, ValidationPipe, Get, Query, Body, Post } from '@nestjs/common';
import { FilterDto } from './dto/filter.dto';
import { ScheduleService } from './schedule.service';
import { ErrorDto } from './dto/error.dto';
import { QueuingService } from './queuing.service';
import { ContinueDto } from './dto/continue.dto';

@Controller('/v0/queuing')
export class QueuingController {
    constructor(private readonly queuingService: QueuingService) { }

    @Post('/review/start')
    start(@Body(ValidationPipe) filterDto: FilterDto) {
        try {
            ScheduleService.queue.push(filterDto);

        } catch (error) {
            console.log('--------------------error--------------------');
            console.log(JSON.stringify(error.response.data, null, 2));
        }
    }

    @Post('/review/continue')
    continue(@Body(ValidationPipe) continueDto: ContinueDto) {
        try {
            continueDto.processed.forEach(element => {
                ScheduleService.queue.push(element);
            });
            ScheduleService.continue = true;
        } catch (error) {
            console.log('--------------------error--------------------');
            console.log(JSON.stringify(error.response.data, null, 2));
        }
    }

    @Post('/review/error')
    async error(@Body(ValidationPipe) errorDto: ErrorDto) {
        // console.log('--------------------error--------------------');
        console.error('error: ', JSON.stringify(errorDto, null, 2));

        try {
            const status = await this.queuingService.pushQueue(errorDto);
            if (status === 201) {
                const { userId, workspaceId } = errorDto;
                const filterDto = { userId, workspaceId };
                ScheduleService.queue.push(filterDto);
            }
        } catch (error) {
            console.log('--------------------error--------------------');
            console.log(JSON.stringify(error.response.data, null, 2));

        }
    }
}
