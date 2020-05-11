import { BaseEntity, Entity, PrimaryGeneratedColumn, Column, OneToMany, CreateDateColumn, UpdateDateColumn } from 'typeorm';
import { UserWorkspace } from './user-workspace.entity';

@Entity({
    schema: 'Toolbox',
    name: 'Permission',
})
export class Permission extends BaseEntity {
    @PrimaryGeneratedColumn()
    id: number;

    @Column('text', { unique: true })
    name: string;

    @Column('boolean', { default: true })
    status: boolean;

    @CreateDateColumn({ name: 'created_at' })
    createdAt: Date;

    @UpdateDateColumn({ name: 'updated_at' })
    updatedAt: Date;

    @Column('timestamp', { name: 'deleted_at', nullable: true })
    deletedAt: Date;

    @OneToMany((type) => UserWorkspace, (userWorkspace) => userWorkspace.permission)
    public userWorkspaces: UserWorkspace[];
}
