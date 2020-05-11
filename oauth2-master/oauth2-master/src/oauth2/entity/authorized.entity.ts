import { BaseEntity, Entity, PrimaryColumn, ManyToOne, Column, JoinColumn } from 'typeorm';
import { Application } from './application.entity';
import { ApiScope } from './apiScope.entity';
import { User } from './user.entity';

@Entity({
    schema: 'Security',
    name: 'Authorized',
})
export class Authorized extends BaseEntity {
    @PrimaryColumn({ name: 'id_user' })
    userId: string;

    @PrimaryColumn({ name: 'id_application' })
    applicationId: string;

    @PrimaryColumn({ name: 'id_api_scope' })
    apiScopeId: number;

    @Column('boolean', { name: 'is_authorized' })
    isAuthorized: boolean;

    @Column('boolean', { default: true })
    status: boolean;

    @ManyToOne(type => Application, application => application.authorizeds)
    @JoinColumn({ name: 'id_application' })
    public application: Application;

    @ManyToOne(type => ApiScope, apiScope => apiScope.authorizeds)
    @JoinColumn({ name: 'id_api_scope' })
    public apiScope: ApiScope;

    @ManyToOne(type => User, user => user.authorizeds)
    @JoinColumn({ name: 'id_user' })
    public user: User;
}
