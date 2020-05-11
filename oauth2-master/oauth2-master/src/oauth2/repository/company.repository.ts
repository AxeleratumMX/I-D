import { EntityRepository, Repository } from 'typeorm';
import { Company } from '../entity/company.entity';

@EntityRepository(Company)
export class CompanyRepository extends Repository<Company> {

}
