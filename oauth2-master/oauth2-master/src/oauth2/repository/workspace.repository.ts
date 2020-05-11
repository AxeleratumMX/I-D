import { EntityRepository, Repository } from 'typeorm';
import { Workspace } from '../entity/workspace.entity';

@EntityRepository(Workspace)
export class WorkspaceRepository extends Repository<Workspace> {

}
