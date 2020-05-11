import { ValidateIf, IsNotEmpty, IsString, IsEmail, Min, Max, IsUrl, IsAlphanumeric, MinLength, MaxLength } from 'class-validator';

export class TokenRequest {
    // tslint:disable-next-line: variable-name
    @IsNotEmpty()
    @IsString()
    // tslint:disable-next-line: variable-name
    grant_type: string;

    @ValidateIf(o => o.grant_type === 'password')
    @IsNotEmpty({ message: 'que es esto' })
    @IsEmail()
    username: string;

    @ValidateIf(o => o.grant_type === 'password')
    @IsNotEmpty()
    @IsString()
    password: string;

    @ValidateIf(o => o.grant_type === 'password')
    @IsNotEmpty()
    @IsString()
    scope: string;

    @ValidateIf(o => (o.grant_type === 'authorization_code') || (o.grant_type === 'refresh_token'))
    @IsNotEmpty()
    @IsString()
    // tslint:disable-next-line: variable-name
    client_id: string;

    @ValidateIf(o => (o.grant_type === 'authorization_code') || (o.grant_type === 'refresh_token'))
    @IsNotEmpty()
    @IsString()
    // tslint:disable-next-line: variable-name
    client_secret: string;

    @ValidateIf(o => o.grant_type === 'authorization_code')
    @IsNotEmpty()
    @IsString()
    @IsUrl()
    // tslint:disable-next-line: variable-name
    redirect_uri: string;

    @ValidateIf(o => o.grant_type === 'authorization_code')
    @IsNotEmpty()
    @IsString()
    code: string;

    @ValidateIf(o => o.grant_type === 'authorization_code')
    @IsNotEmpty()
    @IsString()
    // tslint:disable-next-line: variable-name
    code_verifier: string;

    @ValidateIf(o => o.grant_type === 'refresh_token')
    @IsNotEmpty()
    @IsString()
    // tslint:disable-next-line: variable-name
    refresh_token: string;
}
