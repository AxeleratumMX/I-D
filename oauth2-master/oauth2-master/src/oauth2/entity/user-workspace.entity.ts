import { BaseEntity, Entity, Column, ManyToOne, JoinColumn, OneToMany, PrimaryGeneratedColumn } from 'typeorm';
import { User } from './user.entity';
import { Workspace } from './workspace.entity';
// import { Consumption } from './consumption.entity';
// import { UserWorkspacePipeline } from './user-workspace-pipeline.entity';
import { Permission } from './permission.entity';

@Entity({
    schema: 'Toolbox',
    name: 'User_Workspace',
})

export class UserWorkspace extends BaseEntity {
    @PrimaryGeneratedColumn()
    id: number;

    @Column({ name: 'id_user' })
    userId: string;

    @Column({ name: 'id_workspace' })
    workspaceId: string;

    @Column({ name: 'id_permission' })
    permissionId: number;

    @Column('float', { name: 'max_limit' })
    maxLimit: number;

    @Column('float', { name: 'current_consumption' })
    currentConsumption: number;

    @ManyToOne(type => User, user => user.userWorkspaces)
    @JoinColumn({ name: 'id_user' })
    public user: User;

    @ManyToOne(type => Workspace, workspace => workspace.userWorkspaces)
    @JoinColumn({ name: 'id_workspace' })
    public workspace: Workspace;

    @ManyToOne(type => Permission, permission => permission.userWorkspaces)
    @JoinColumn({ name: 'id_permission' })
    public permission: Permission;

    // @OneToMany((type) => Consumption, (consumption) => consumption.userWorkspace)
    // public consumptions: Consumption[];

    // @OneToMany((type) => UserWorkspacePipeline, (userWorkspacePipeline) => userWorkspacePipeline.userWorkspace)
    // public userWorkspacePipelines: UserWorkspacePipeline[];
}
