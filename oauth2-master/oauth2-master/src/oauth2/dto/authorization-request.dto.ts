import { IsString, IsNotEmpty, Equals, IsUrl, IsOptional, Matches, IsEmpty, IsIn } from 'class-validator';
import { User } from '../entity/user.entity';
// import { Expose } from 'class-transformer';

export class AuthorizationRequest {


    @IsOptional()
    @Matches(/^[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$/, { message: 'Invalid or corrupted Token_id ' })
    token_id: string;

    @IsNotEmpty()
    @IsString()
    @Equals('code', { message: 'This field needs to be set to code' })
    response_type: string;

    @IsNotEmpty()
    @IsString()
    client_id: string;

    @IsNotEmpty()
    @IsString()
    @IsUrl()
    redirect_uri: string;

    @IsNotEmpty()
    @IsString()
    code_challenge: string;

    @IsNotEmpty()
    @IsString()
    @IsIn(['plain', 'S256'])
    code_challenge_method: string = 'plain';

    @IsNotEmpty()
    @IsString()
    scope: string;

    @IsNotEmpty()
    @IsString()
    state: string;
}
