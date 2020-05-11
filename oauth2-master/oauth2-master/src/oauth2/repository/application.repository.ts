import { EntityRepository, Repository } from 'typeorm';
import { Application } from '../entity/application.entity';
import { TokenRequest } from '../dto/token-request.dto';

@EntityRepository(Application)
export class ApplicationRepository extends Repository<Application> {
    async validateApplication(tokenRequest: TokenRequest): Promise<Application> {
        const { client_id: id } = tokenRequest;
        const application = await this.findOne({ id });

        if (application) {
            return application;
        } else {
            return null;
        }
    }
}
