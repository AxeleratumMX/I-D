import { EntityRepository, Repository } from 'typeorm';
import { Connotation } from '../entity/connotation.entity';

@EntityRepository(Connotation)
export class ConnotationRepository extends Repository<Connotation> {
    async authorize() {
        const dummy = new Connotation();
        return dummy;
    }

}
