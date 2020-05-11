import { BaseEntity, Entity, PrimaryColumn, ManyToOne, JoinColumn, Column } from 'typeorm';
import { User } from './user.entity';
import { Company } from './company.entity';

@Entity({
    schema: 'Vili',
    name: 'User_Company',
})

export class UserCompany extends BaseEntity {
    @PrimaryColumn({ name: 'id_user' })
    userId: string;

    @PrimaryColumn({ name: 'id_company' })
    companyId: string;

    @Column('text', { name: 'employee_position' })
    employeePosition: string;

    @ManyToOne(type => User, user => user.userCompanies)
    @JoinColumn({ name: 'id_user' })
    public user: User;

    @ManyToOne(type => Company, company => company.userCompanys)
    @JoinColumn({ name: 'id_company' })
    public company: Company;
}
