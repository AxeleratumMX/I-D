import { IsString, IsNotEmpty, Equals, IsUrl, IsOptional, Matches, MinLength, MaxLength, IsEmail, ValidateIf, IsDefined } from 'class-validator';

import { PASSWORD_REGEX, PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH } from '../../config/validation.config';
// import { Expose } from 'class-transformer';

export class RegistrationRequest {

    @IsNotEmpty()
    @IsString()
    @IsEmail()
    email: string;

    @IsNotEmpty()
    @MinLength(PASSWORD_MIN_LENGTH)
    @MaxLength(PASSWORD_MAX_LENGTH)
    @Matches(PASSWORD_REGEX, { message: 'Password too weak.' })
    password: string;

    @ValidateIf(o => o.password !== o.passwordConfirmation)
    @IsDefined()
    @IsNotEmpty()
    @Matches(/^$/, { message: 'Password and confirmation doesn\'t match.' })
    passwordConfirmation: string;

    @IsNotEmpty()
    @IsString()
    name: string;
}
