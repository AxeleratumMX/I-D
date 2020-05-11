import { Injectable, HttpService } from '@nestjs/common';
const url = require('url');

@Injectable()
export class QueuingService {
    constructor(
        private readonly httpService: HttpService,
    ) { }
    async pushQueue(data): Promise<number> {
        const response = await this.httpService.post(
            // tslint:disable-next-line: max-line-length
            url.resolve('http://192.168.15.135:8000', '/v0/queue/review/push'), data,

            // url.resolve(process.env.API_PROTOCOL + '://' + process.env.API_HOST + ':' + process.env.API_PORT, '/v0/queue/review/push'), data,
        ).toPromise();
        return response.status;
    }
}
