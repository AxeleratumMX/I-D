import { EntityRepository, Repository } from 'typeorm';
import { UserCompany } from '../entity/user-company.entity';

@EntityRepository(UserCompany)
export class UserCompanyRepository extends Repository<UserCompany> {

}
