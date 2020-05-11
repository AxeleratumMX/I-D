import { BaseEntity, Entity, PrimaryGeneratedColumn, Column, Timestamp, Unique, OneToMany, CreateDateColumn, UpdateDateColumn } from 'typeorm';
import { UserApplication } from './user-application.entity';
import { ApplicationApiScope } from './application-apiScope.entity';
import { Authorized } from './authorized.entity';

@Entity({
    schema: 'Vili',
    name: 'Application',
})
export class Application extends BaseEntity {
    @PrimaryGeneratedColumn('uuid')
    id: string;

    @Column('text')
    name: string;

    @Column('text', { name: 'redirect_uri' })
    redirectUri: string;

    @Column('text')
    secret: string;

    @CreateDateColumn({ name: 'created_at' })
    createdAt: Date;

    @UpdateDateColumn({ name: 'updated_at' })
    updatedAt: Date;

    @Column('timestamp', { name: 'deleted_at', nullable: true })
    deletedAt: Date;

    @Column('boolean', { default: true })
    status: boolean;

    @OneToMany((type) => UserApplication, (userApplication) => userApplication.application)
    public userApplications: UserApplication[];

    @OneToMany((type) => ApplicationApiScope, (applicationApiScopes) => applicationApiScopes.application)
    public applicationApiScopes: ApplicationApiScope[];

    @OneToMany((type) => Authorized, (authorized) => authorized.application)
    public authorizeds: Authorized[];
}
