import { BaseEntity, Entity, PrimaryGeneratedColumn, Column, OneToMany, CreateDateColumn, UpdateDateColumn } from 'typeorm';
import { UserApplication } from './user-application.entity';
import { Authorized } from './authorized.entity';
// import { UserCompany } from './user-company.entity';
import { UserWorkspace } from './user-workspace.entity';
import { UserCompany } from './user-company.entity';
import { Token } from './token.entity';

@Entity({
    schema: 'Vili',
    name: 'User',
})
export class User extends BaseEntity {
    @PrimaryGeneratedColumn('uuid')
    id: string;

    @Column('text', { unique: true })
    email: string;

    @Column('text')
    password: string;

    @Column('text', { nullable: true })
    phone: string;

    @Column('text', { nullable: true })
    name: string;

    @Column('text', { nullable: true })
    surname: string;

    @Column('text', { nullable: true })
    country: string;

    @CreateDateColumn({ name: 'created_at' })
    createdAt: Date;

    @UpdateDateColumn({ name: 'updated_at' })
    updatedAt: Date;

    @Column('timestamp', { name: 'deleted_at', nullable: true })
    deletedAt: Date;

    @Column('boolean', { default: true })
    status: boolean;

    @OneToMany((type) => UserApplication, (userApplication) => userApplication.user)
    public userApplications: UserApplication[];

    @OneToMany((type) => UserCompany, (userCompany) => userCompany.user)
    public userCompanies: UserCompany[];

    @OneToMany((type) => UserWorkspace, (userWorkspace) => userWorkspace.user)
    public userWorkspaces: UserWorkspace[];

    @OneToMany((type) => Authorized, (authorized) => authorized.user)
    public authorizeds: Authorized[];

    @OneToMany((type) => Token, (token) => token.user)
    public token: Token;

    // async validatePassword(password: string): Promise<boolean> {
    //     const hash = await bcrypt.hash(password, this.salt);
    //     return hash === this.password;
    // }
}
