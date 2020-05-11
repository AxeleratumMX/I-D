import { Injectable, NestMiddleware, Redirect } from '@nestjs/common';
import { Request, Response } from 'express';

@Injectable()
export class AuthorizeMiddleware implements NestMiddleware {
    // @Redirect('https://vili.tech/login', 302)
    use(req: Request, res: Response, next: Function) {
        // console.log(req.query.token_id);


        if (req.query.token_id) {
            next();
        }
        else {
            const url = 'https://vili.tech/login/' +
                '?token_id=' + req.query.token_id +
                '&response_type=' + req.query.response_type +
                '&client_id=' + req.query.client_id +
                '&redirect_uri=' + req.query.redirect_uri +
                '&code_challenge=' + req.query.code_challenge +
                '&code_challenge_method=' + req.query.code_challenge_method +
                '&scope=' + req.query.scope +
                '&state=' + req.query.state;
            const statusCode = 302;
            res.redirect(statusCode, url);
        }

    }
}
