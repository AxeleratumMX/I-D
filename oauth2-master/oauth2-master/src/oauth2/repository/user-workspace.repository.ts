import { EntityRepository, Repository } from 'typeorm';
import { UserWorkspace } from '../entity/user-workspace.entity';

@EntityRepository(UserWorkspace)
export class UserWorkspaceRepository extends Repository<UserWorkspace> {

}
