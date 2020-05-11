import { BaseEntity, Entity, PrimaryGeneratedColumn, Column, Unique, Timestamp, OneToMany, CreateDateColumn, UpdateDateColumn } from 'typeorm';
import { UserCompany } from './user-company.entity';

@Entity({
    schema: 'Vili',
    name: 'Company',
})
export class Company extends BaseEntity {
    @PrimaryGeneratedColumn('uuid')
    id: string;

    @Column('text', { unique: true })
    name: string;

    @Column('text')
    phone: string;

    @Column('text')
    email: string;

    @Column('text', { name: 'address_1' })
    address1: string;

    @Column('text', { name: 'address_2', nullable: true })
    address2: string;

    @Column('text')
    city: string;

    @Column('text')
    state: string;

    @Column('text')
    zip: string;

    @Column('text')
    country: string;

    @Column('boolean', { default: true })
    status: boolean;

    @CreateDateColumn({ name: 'created_at' })
    createdAt: Date;

    @UpdateDateColumn({ name: 'updated_at' })
    updatedAt: Date;

    @Column('timestamp', { name: 'deleted_at', nullable: true })
    deletedAt: Date;

    @OneToMany((type) => UserCompany, (userCompany) => userCompany.user)
    public userCompanys: UserCompany[];
}
