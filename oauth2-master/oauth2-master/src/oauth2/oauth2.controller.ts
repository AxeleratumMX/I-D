import { Controller, Get, Post, Body, ValidationPipe, Redirect, Query, Header, BadRequestException, UseGuards, UnauthorizedException, ForbiddenException, InternalServerErrorException } from '@nestjs/common';
import { Oauth2Service } from './oauth2.service';
import { AuthorizationResponse } from './dto/authorization-response.dto';
import { promises } from 'fs';
import { TokenResponse } from './dto/token-response.dto';
import { AuthorizationRequest } from './dto/authorization-request.dto';
import { IsOptional, ValidateNested } from 'class-validator';
import { logicalExpression } from '@babel/types';
import { AuthenticationRequest } from './dto/authentication-request.dto';
import { RegistrationRequest } from './dto/registration-request.dto';
import { TokenRequest } from './dto/token-request.dto';
import { Observable } from 'rxjs';
import { AxiosResponse } from 'axios';
import { map } from 'rxjs/operators';
import { AuthGuard } from '@nestjs/passport';
import { GetUser } from './decorator/get-user.decorator';
import { User } from './entity/user.entity';
import { JwtService } from '@nestjs/jwt';

@Controller('/v0/oauth2')
export class Oauth2Controller {
    constructor(
        private oauth2Service: Oauth2Service,
        private jwtService: JwtService,
    ) { }

    @Post('/signup')
    async signUp(@Body(ValidationPipe) registrationRequest: RegistrationRequest) {
        return await this.oauth2Service.signUp(registrationRequest);
    }

    @Get('/authorize')
    @UseGuards(AuthGuard())
    // @Redirect('https://vili.tech/login', 302)
    authorize(
        @Query(ValidationPipe) authorizationRequest: AuthorizationRequest,
        @GetUser() user: User,
    ) {
        return this.oauth2Service.validateApplication(authorizationRequest);
    }

    @Post('/token')
    @Header('Cache-Control', 'no-store')
    @Header('Pragma', 'no-cache')
    // @Header('Access-Control-Allow-Origin', 'https://vili.tech')
    @Header('Access-Control-Allow-Origin', '*')
    token(@Body(ValidationPipe) tokenRequest: TokenRequest): Promise<TokenResponse> {
        // console.log('token');
        switch (tokenRequest.grant_type) {
            case 'password':
                console.log('password');

                return this.oauth2Service.signIn(tokenRequest);
                break;
            case 'authorization_code':
                return this.oauth2Service.token(tokenRequest);
                break;
            case 'refresh_token':
                console.log('refresh_token');
                // const refreshToken = this.jwtService.decode(tokenRequest.refresh_token);
                // console.log(refreshToken);
                return this.oauth2Service.refreshToken(tokenRequest);
                break;

            default:
                throw new BadRequestException({ statusCode: '400', error: 'unsupported_grant_type', message: 'grant_type parameter needs to be one of these [password, authorization_code, refresh_token]' });
                break;
        }
        // if (tokenRequest.grant_type === 'password') {
        //     console.log(this.oauth2Service.makeid(128));
        //     console.log('authorization_code');
        //     return this.oauth2Service.signIn(tokenRequest);
        // } else if (tokenRequest.grant_type === 'authorization_code') {
        //     console.log('authorization_code');
        //     return this.oauth2Service.token(tokenRequest);
        // } else if (tokenRequest.grant_type === 'refresh_token') {
        //     console.log('refresh_token');
        //     const refreshToken = this.jwtService.decode(tokenRequest.refresh_token);
        //     console.log(refreshToken);

        //     // return this.oauth2Service.refreshToken(tokenRequest);
        // } else {
        //     console.log('else');

        //     // tslint:disable-next-line: max-line-length
        //     // tslint:disable-next-line: no-unused-expression
        //     // tslint:disable-next-line: max-line-length
        //     throw new BadRequestException({ statusCode: '400', error: 'unsupported_grant_type', message: 'grant_type parameter needs to be one of these [password, authorization_code, refresh_token]' });
        // }
        // return tokenResponse;
    }

}
