import { BaseEntity, Entity, PrimaryColumn, ManyToOne, JoinColumn } from 'typeorm';
import { User } from './user.entity';
import { Application } from './application.entity';
import { Connotation } from './connotation.entity';

@Entity({
    schema: 'Vili',
    name: 'User_Application',
})

export class UserApplication extends BaseEntity {
    @PrimaryColumn({ name: 'id_user' })
    userId: string;

    @PrimaryColumn({ name: 'id_application' })
    applicationId: string;

    @PrimaryColumn({ name: 'id_connotation' })
    connotationId: number;

    @ManyToOne(type => User, user => user.userApplications)
    @JoinColumn({ name: 'id_user' })
    public user: User;

    @ManyToOne(type => Application, application => application.userApplications)
    @JoinColumn({ name: 'id_application' })
    public application: Application;

    @ManyToOne(type => Connotation, connotation => connotation.userApplications)
    @JoinColumn({ name: 'id_connotation' })
    public connotation: Connotation;
}
