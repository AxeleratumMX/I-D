import { EntityRepository, Repository } from 'typeorm';
import { Authorization } from '../entity/authorization.entity';

@EntityRepository(Authorization)
export class AuthorizationRepository extends Repository<Authorization>{
    async authorize() {
        const dummy = new Authorization();
        return dummy;
    }

}
