import { PassportStrategy } from '@nestjs/passport';
import { Strategy, ExtractJwt } from 'passport-jwt';
import { Injectable, UnauthorizedException, BadRequestException } from '@nestjs/common';
import { JwtIdToken } from './jwt-idToken.interface';
import { InjectRepository } from '@nestjs/typeorm';
import { UserRepository } from './repository/user.repository';
import { jwtConstants } from './jwt-constants';
import { validate } from '@babel/types';

@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
    constructor(
        @InjectRepository(UserRepository)
        private userRepository: UserRepository,
    ) {
        super({
            jwtFromRequest: ExtractJwt.fromUrlQueryParameter('token_id'),
            secretOrKey: jwtConstants.publicKey,
        });

    }

    async validate(payload: JwtIdToken, done) {
        console.log(done);

        const { userId: id } = payload;
        const user = await this.userRepository.findOne({ id });
        if (!user) {
            throw new BadRequestException();
        }
        return user;
    }
}
