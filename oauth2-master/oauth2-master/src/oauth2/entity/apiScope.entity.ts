import { BaseEntity, Entity, PrimaryGeneratedColumn, Column, Unique, OneToMany } from 'typeorm';
import { ApplicationApiScope } from './application-apiScope.entity';
import { Authorized } from './authorized.entity';
// import { Consumption } from './consumption.entity';
// import { PipelineApiScope } from './pipeline-apiScope.entity';

@Entity({
    schema: 'Vili',
    name: 'ApiScope',
})
export class ApiScope extends BaseEntity {
    @PrimaryGeneratedColumn()
    id: number;

    @Column('text', { unique: true })
    modifier: string;

    @Column('text', { unique: true })
    uri: string;

    @Column('text')
    layer: string;

    @Column('text')
    description: string;

    @Column('boolean', { name: 'is_public' })
    isPublic: boolean;

    @Column('boolean', { default: true })
    status: boolean;

    @OneToMany((type) => ApplicationApiScope, (applicationApiScopes) => applicationApiScopes.apiScope)
    public applicationApiScopes: ApplicationApiScope[];

    // @OneToMany((type) => PipelineApiScope, (pipelineApiScope) => pipelineApiScope.apiScope)
    // public pipelineApiScopes: PipelineApiScope[];

    // @OneToMany((type) => Consumption, (consumption) => consumption.apiScope)
    // public consumptions: Consumption[];

    @OneToMany((type) => Authorized, (authorized) => authorized.apiScope)
    public authorizeds: Authorized[];
}
