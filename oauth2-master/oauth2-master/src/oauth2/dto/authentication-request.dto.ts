import { IsString, IsNotEmpty, Equals, IsUrl, IsOptional, Matches } from 'class-validator';
// import { Expose } from 'class-transformer';

export class AuthenticationRequest {

    // @Expose({ name: "response_type" })
    @IsNotEmpty()
    @IsString()
    @Equals('password')
    grantType: string;

    // @Expose({ name: "client_id" })
    @IsNotEmpty()
    @IsString()
    applicationId: string;

    // @Expose({ name: "redirect_uri" })
    @IsNotEmpty()
    @IsString()
    @IsUrl()
    redirectUri: string;

    @IsNotEmpty()
    @IsString()
    email: string;

    @IsNotEmpty()
    @IsString()
    password: string;

    // @Expose({ name: "scope" })
    @IsNotEmpty()
    @IsString()
    apiScope: string;
}
