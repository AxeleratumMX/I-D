import { BaseEntity, Entity, PrimaryGeneratedColumn, Column, OneToMany, CreateDateColumn, UpdateDateColumn } from 'typeorm';
import { UserApplication } from './user-application.entity';

@Entity({
    schema: 'Vili',
    name: 'Connotation',
})
export class Connotation extends BaseEntity {
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

    @OneToMany((type) => UserApplication, (userApplication) => userApplication.connotation)
    public userApplications: UserApplication[];
}
