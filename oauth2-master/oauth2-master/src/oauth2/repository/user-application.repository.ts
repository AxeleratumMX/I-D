import { EntityRepository, Repository } from 'typeorm';
import { UserApplication } from '../entity/user-application.entity';

@EntityRepository(UserApplication)
export class UserApplicationRepository extends Repository<UserApplication>{

}
