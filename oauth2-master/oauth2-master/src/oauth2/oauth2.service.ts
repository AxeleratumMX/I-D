import { Injectable, HttpService } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { JwtService } from '@nestjs/jwt';
import { JwtIdToken } from './jwt-idToken.interface';
import { JwtAccessToken } from './jwt-accessToken.interface';
import { JwtRefreshToken } from './jwt-refreshToken.interface';
import { ApiScopeRepository } from './repository/apiScope.repository';
import { ApplicationApiScopeRepository } from './repository/application-apiscope.repository';
import { ApplicationRepository } from './repository/application.repository';
import { AuthorizedRepository } from './repository/authorized.repository';
import { ConnotationRepository } from './repository/connotation.repository';
import { TokenRepository } from './repository/token.repository';
import { UserApplicationRepository } from './repository/user-application.repository';
import { UserRepository } from './repository/user.repository';
import { AuthorizationRequest } from './dto/authorization-request.dto';
import { RegistrationRequest } from './dto/registration-request.dto';
import { TokenRequest } from './dto/token-request.dto';
import { TokenResponse } from './dto/token-response.dto';
import { resolve } from 'path';

@Injectable()
export class Oauth2Service {
    constructor(
        @InjectRepository(ApiScopeRepository)
        private apiScopeRepository: ApiScopeRepository,
        @InjectRepository(ApplicationApiScopeRepository)
        private applicationApiScopeRepository: ApplicationApiScopeRepository,
        @InjectRepository(ApplicationRepository)
        private applicationRespository: ApplicationRepository,
        @InjectRepository(AuthorizedRepository)
        private authorizedRepository: AuthorizedRepository,
        @InjectRepository(ConnotationRepository)
        private connotationRepository: ConnotationRepository,
        @InjectRepository(TokenRepository)
        private tokenRepository: TokenRepository,
        @InjectRepository(UserApplicationRepository)
        private userApplicationRepository: UserApplicationRepository,
        @InjectRepository(UserRepository)
        private userRepository: UserRepository,
        private jwtService: JwtService,
        private readonly httpService: HttpService,
    ) { }

    async signUp(registrationRequest: RegistrationRequest): Promise<void> {
        // return this.userRepository.signUp(registrationRequest);
        const data = {
            email: registrationRequest.email,
            password: registrationRequest.password,
            passwordConfirmation: registrationRequest.passwordConfirmation,
            name: registrationRequest.name,
        };
        const url = require('url');
        const res = await this.httpService.post(
            // tslint:disable-next-line: max-line-length
            url.resolve(process.env.API_PROTOCOL + '://' + process.env.API_HOST + ':' + process.env.API_PORT, '/v0/user'),
            data,
        ).toPromise();
    }

    async signIn(tokenRequest: TokenRequest): Promise<any> {
        console.log('entre');
        return await this.userRepository.validateUserPassword(tokenRequest)
            .then(
                async (userId) => {
                    console.log(userId);

                    return await this.tokenRepository.generateToken(userId);
                },
            )
            .then(

                (generatedToken) => {
                    console.log('generatedToken', generatedToken);

                    // this.tokenRepository.updateToken(generatedToken, userId);
                    // tslint:disable-next-line: max-line-length
                    const { userId, accessToken: accessTokenId, tokenType: token_type, atExpiresIn: expires_in, refreshToken: refreshTokenId } = generatedToken;
                    const scope = [''];
                    const jwtTokenId: JwtIdToken = { userId };
                    const jwtAccessToken: JwtAccessToken = { scope };
                    const jwtRefreshToken: JwtRefreshToken = {};
                    const id_token = this.jwtService.sign(jwtTokenId, { noTimestamp: true });
                    const access_token = this.jwtService.sign(jwtAccessToken, { jwtid: accessTokenId, expiresIn: '10m' });
                    const refresh_token = this.jwtService.sign(jwtRefreshToken, { jwtid: refreshTokenId, expiresIn: '1d' });
                    const tokenResponse: TokenResponse = { id_token, access_token, token_type, expires_in, refresh_token, scope };
                    return tokenResponse;
                },
            );
        // return await Promise.all([
        //     this.userRepository.validateUserPassword(tokenRequest),
        //     this.tokenRepository.generateToken(),
        // ]).then(
        //     async (results) => {
        //         const userId = results[0];
        //         const generatedToken = results[1];
        //         await this.tokenRepository.updateToken(generatedToken, userId);
        //         const { accessToken: accessTokenId, tokenType: token_type, atExpiresIn: expires_in, refreshToken: refreshTokenId } = generatedToken;
        //         const scope = [''];
        //         const jwtTokenId: JwtIdToken = { userId };
        //         const jwtAccessToken: JwtAccessToken = { scope };
        //         const jwtRefreshToken: JwtRefreshToken = {};
        //         const id_token = this.jwtService.sign(jwtTokenId, { noTimestamp: true });
        //         const access_token = this.jwtService.sign(jwtAccessToken, { jwtid: accessTokenId, expiresIn: '10m' });
        //         const refresh_token = this.jwtService.sign(jwtRefreshToken, { jwtid: refreshTokenId, expiresIn: '1d' });
        //         const tokenResponse: TokenResponse = { id_token, access_token, token_type, expires_in, refresh_token, scope };
        //         return tokenResponse;
        //     },
        // );
    }
    async token(tokenRequest: TokenRequest): Promise<TokenResponse> {
        // const tokenResponse = new TokenResponse();
        // tokenResponse.access_token = 'algun token';
        // return tokenResponse;
        return new TokenResponse;
    }

    async refreshToken(tokenRequest: TokenRequest): Promise<TokenResponse> {
        console.log(this.jwtService.decode(tokenRequest.refresh_token)['jti']);

        return await this.tokenRepository.refreshToken(this.jwtService.decode(tokenRequest.refresh_token)['jti'])
            .then(
                (generatedToken) => {
                    const { accessToken: accessTokenId, tokenType: token_type, atExpiresIn: expires_in, refreshToken: refreshTokenId } = generatedToken;
                    const scope = [''];
                    const jwtAccessToken: JwtAccessToken = { scope };
                    const jwtRefreshToken: JwtRefreshToken = {};
                    const access_token = this.jwtService.sign(jwtAccessToken, { jwtid: accessTokenId, expiresIn: '10m' });
                    const refresh_token = this.jwtService.sign(jwtRefreshToken, { jwtid: refreshTokenId, expiresIn: '1d' });
                    const tokenResponse: TokenResponse = { access_token, token_type, expires_in, refresh_token, scope };
                    return tokenResponse;
                },
            );

        // const tokenResponse = new TokenResponse();
        // tokenResponse.access_token = 'algun token';
        // return tokenResponse;
        return new TokenResponse;
    }

    async validateApplication(
        authorizationRequest: AuthorizationRequest): Promise<object> {
        const { client_id: id } = authorizationRequest;
        const application = await this.applicationRespository.findOne({ id });
        if (application) {
            return {
                url: 'http://vili.tech/authorize/' +
                    '?token_id=' + authorizationRequest.token_id +
                    '&response_type=' + authorizationRequest.response_type +
                    '&client_id=' + authorizationRequest.client_id +
                    '&redirect_uri=' + authorizationRequest.redirect_uri +
                    '&code_challenge=' + authorizationRequest.code_challenge +
                    '&code_challenge_method=' + authorizationRequest.code_challenge_method +
                    '&scope=' + authorizationRequest.scope +
                    '&state=' + authorizationRequest.state,
                statusCode: 302,
            };
        } else {
            return {
                url: 'https://vili.tech/validation/' +
                    '?token_id=' + authorizationRequest.token_id +
                    '&response_type=' + authorizationRequest.response_type +
                    '&client_id=' + authorizationRequest.client_id +
                    '&redirect_uri=' + authorizationRequest.redirect_uri +
                    '&code_challenge=' + authorizationRequest.code_challenge +
                    '&code_challenge_method=' + authorizationRequest.code_challenge_method +
                    '&scope=' + authorizationRequest.scope +
                    '&state=' + authorizationRequest.state,
                statusCode: 302,
            };
        }
    }

    makeid(length) {
        let result = '';
        const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        const charactersLength = characters.length;
        for (let i in length) {
            result += characters.charAt(Math.floor(Math.random() * charactersLength));
        }
        return result;
    }



    // async authorize(
    //     response_type: string,q
    //     client_id: string,
    //     redirect_uri: string,
    //     code_challenge: string,
    //     code_challenge_method: string,
    //     scope: string,
    //     state: string,
    // ): Promise<AuthorizationResponse> {
    //     const application = await this.applicationRespository.findOne({ where: { client_id } });

    //     if (application) {
    //         //generate code
    //     }
    //     const authorizationResponse = new AuthorizationResponse();
    //     authorizationResponse.code = 'example code'; //generated code
    //     authorizationResponse.state = state;
    //     return authorizationResponse;
    // }
}