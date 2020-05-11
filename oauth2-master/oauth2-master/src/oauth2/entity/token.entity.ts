import { BaseEntity, Entity, PrimaryGeneratedColumn, Column, CreateDateColumn, Generated, UpdateDateColumn, OneToOne, JoinColumn, PrimaryColumn } from 'typeorm';
import { User } from './user.entity';

@Entity({
    schema: 'Security',
    name: 'Token',
})

export class Token extends BaseEntity {

    @PrimaryColumn('uuid', { name: 'id_user' })
    userId: string;

    @Column('uuid', { name: 'access_token' })
    @Generated('uuid')
    accessToken: string;

    @Column('text', { name: 'token_type', default: 'bearer' })
    tokenType: string;

    @UpdateDateColumn({ name: 'at_created_at' })
    atCreatedAt: Date;

    @Column('interval', { name: 'at_expires_in', default: '10 minutes' })
    atExpiresIn: string;

    @Column('uuid', { name: 'refresh_token' })
    @Generated('uuid')
    refreshToken: string;

    @UpdateDateColumn({ name: 'rt_created_at' })
    rtCreatedAt: Date;

    @Column('interval', { name: 'rt_expires_in', default: '1 day' })
    rtExpiresIn: string;

    @Column('boolean', { default: true })
    status: boolean;

    @OneToOne(type => User, user => user.token)
    @JoinColumn({ name: 'id_user' })
    public user: User;
}
