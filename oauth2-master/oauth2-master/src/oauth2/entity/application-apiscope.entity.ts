import { BaseEntity, Entity, PrimaryColumn, ManyToOne, Column, JoinColumn } from 'typeorm';
import { Application } from './application.entity';
import { ApiScope } from './apiScope.entity';

@Entity({
    schema: 'Vili',
    name: 'Application_ApiScope',
})
export class ApplicationApiScope extends BaseEntity {
    @PrimaryColumn({ name: 'id_application' })
    applicationId: string;

    @PrimaryColumn({ name: 'id_api_scope' })
    apiScopeId: number;

    @Column('boolean', { name: 'is_for_user' })
    isForUser: boolean;

    @ManyToOne(type => Application, application => application.applicationApiScopes)
    @JoinColumn({ name: 'id_application' })
    application: Application;

    @ManyToOne(type => ApiScope, apiScope => apiScope.applicationApiScopes)
    @JoinColumn({ name: 'id_api_scope' })
    apiScope: ApiScope;

}
