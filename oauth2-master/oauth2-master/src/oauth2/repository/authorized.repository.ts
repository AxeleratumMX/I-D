import { EntityRepository, Repository } from 'typeorm';
import { Authorized } from '../entity/authorized.entity';


@EntityRepository(Authorized)
export class AuthorizedRepository extends Repository<Authorized>{
    async authorize() {
        const dummy = new Authorized();
        return dummy;
    }

}
