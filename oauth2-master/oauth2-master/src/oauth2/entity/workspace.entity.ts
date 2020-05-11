import { BaseEntity, Entity, PrimaryGeneratedColumn, Column, Unique, Timestamp, OneToMany, CreateDateColumn, UpdateDateColumn } from 'typeorm';
import { UserWorkspace } from './user-workspace.entity';

@Entity({
    schema: 'Toolbox',
    name: 'Workspace',
})
export class Workspace extends BaseEntity {
    @PrimaryGeneratedColumn('uuid')
    id: string;

    @Column('text', { unique: true })
    name: string;

    @Column('float', { name: 'max_limit' })
    maxLimit: number;

    @Column('float', { name: 'current_consumption' })
    currentConsumption: number;

    @CreateDateColumn({ name: 'created_at' })
    createdAt: Date;

    @UpdateDateColumn({ name: 'updated_at' })
    updatedAt: Date;

    @Column('timestamp', { name: 'deleted_at', nullable: true })
    deletedAt: Date;

    @Column('boolean', { default: true })
    status: boolean;

    @OneToMany((type) => UserWorkspace, (userWorkspace) => userWorkspace.user)
    public userWorkspaces: UserWorkspace[];
}
