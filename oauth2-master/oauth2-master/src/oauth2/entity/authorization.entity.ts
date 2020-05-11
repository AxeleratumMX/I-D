import { BaseEntity, Entity, PrimaryColumn, ManyToOne, Column, JoinColumn, PrimaryGeneratedColumn } from 'typeorm';

@Entity({
    schema: 'Security',
    name: 'Authorization',
})
export class Authorization extends BaseEntity {
    @PrimaryGeneratedColumn('uuid')
    id: string;

    @Column('text', { name: 'code_challenge' })
    codeChallenge: string;

    @Column('text', { name: 'code_challenge_method' })
    codeChallengeMethod: string;

    @Column('text', { name: 'authorization_code' })
    authorizationCode: string;

    @Column('text', { name: 'redirect_uri' })
    redirectUri: string;

    @Column('text', { name: 'api_scopes' })
    apiScope: string;
}
