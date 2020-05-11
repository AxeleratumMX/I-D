import { Injectable, NestMiddleware, Redirect, UnauthorizedException } from '@nestjs/common';
import { Request, Response } from 'express';
import { JwtService } from '@nestjs/jwt';
import { JsonWebTokenError, TokenExpiredError } from 'jsonwebtoken';
import { throwError } from 'rxjs';

@Injectable()
export class RefreshMiddleware implements NestMiddleware {
    constructor(
        private jwtService: JwtService,
    ) { }
    // @Redirect('https://vili.tech/login', 302)
    use(req: Request, res: Response, next: Function) {
        // console.log(req.body.refresh_token);
        const tokenRequest = req.body;

        if (req.body.grant_type === 'refresh_token') {
            try {
                const refreshToken = this.jwtService.verify(tokenRequest.refresh_token, { issuer: 'vili.tech', algorithms: ['RS256'] });

                if (refreshToken.scope) {
                    throw new JsonWebTokenError('unexpected claim "scope"');
                }
                if (!refreshToken.exp) {
                    throw new JsonWebTokenError('no expiration provided');
                }
                next();
            } catch (error) {
                res.statusCode = 401;
                switch (error.constructor) {
                    case JsonWebTokenError:
                        res.send({ error: 'invalid_token', message: 'The refresh token is invalid (' + error.message + ').' });
                        break;
                    case TokenExpiredError:
                        res.send({ error: 'invalid_token', message: 'The refresh token expired (' + error.message + ').' });
                        break;
                    default:
                        res.send({ error: 'invalid_token', message: error.message });
                        break;
                }
            }
        } else {
            next();
        }

    }
}
