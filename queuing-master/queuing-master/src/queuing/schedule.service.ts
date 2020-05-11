import { Injectable, HttpService } from '@nestjs/common';
import { Interval, Timeout, Cron, NestSchedule } from 'nest-schedule';
const url = require('url');

@Injectable()
export class ScheduleService extends NestSchedule {
    constructor(
        private readonly httpService: HttpService,
    ) { super(); }

    static queue = [];
    static continue = true;
    @Interval(100, { key: 'schedule-interval' })
    async interval(): Promise<void> {
        if (ScheduleService.queue.length > 0 && ScheduleService.continue) {
            const job = ScheduleService.queue.shift();
            const data = {
                userId: job.userId,
                resourceId: job.resourceId,
                bufferSize: 1,
                // frameId: filterDto.frameId,
            };
            const reviews = await this.httpService.post(
                // tslint:disable-next-line: max-line-length
                url.resolve('http://192.168.15.135:8000', '/v0/queue/review/pop'), data,
                // url.resolve(process.env.API_PROTOCOL + '://' + process.env.API_HOST + ':' + process.env.API_PORT, '/v0/queue/review/pop'), data,
            ).toPromise();

            if (reviews.data.length > 0) {
                const chunks = {
                    chunks: reviews.data,
                    // tslint:disable-next-line: max-line-length
                    finishCallbackUrl: process.env.API_PROTOCOL + '://' + process.env.API_HOST + ':' + process.env.API_PORT + '/v0/queuing/review/continue',
                    // finishCallbackUrl: process.env.API_PROTOCOL + '://' + process.env.API_HOST + ':' + process.env.API_PORT + '/v0/queuing/review/continue',
                    // tslint:disable-next-line: max-line-length
                    errorCallbackUrl: process.env.API_PROTOCOL + '://' + process.env.API_HOST + ':' + process.env.API_PORT + '/v0/queuing/review/error',
                };
                const response = this.httpService.post(
                    // tslint:disable-next-line: max-line-length
                    url.resolve(process.env.API_PROTOCOL + '://' + process.env.API_HOST + ':' + process.env.API_PORT, '/v0/pipeline/polarity/execute'), chunks,
                ).toPromise();
                ScheduleService.continue = false;
            }
        }
    }
}
