import { EntityRepository, Repository } from 'typeorm';
import { Token } from '../entity/token.entity';
import * as uuidv4 from 'uuid/v4';
import { TokenRequest } from '../dto/token-request.dto';
import { ConflictException, InternalServerErrorException, UnauthorizedException } from '@nestjs/common';
import { jwtConstants } from '../jwt-constants';

@EntityRepository(Token)
export class TokenRepository extends Repository<Token> {
    async validateToken(tokenRequest: TokenRequest) {
        // const exists = 
    }

    async refreshToken(refreshToken: string): Promise<Token> {
        const token = await this.findOne({ refreshToken });
        token.accessToken = uuidv4();
        token.refreshToken = uuidv4();
        token.save();
        return token;

        // if (token) {
        //     token.accessToken = uuidv4();
        //     token.refreshToken = uuidv4();
        //     console.log('creating token');

        //     token.save();
        //     console.log('token saved');
        //     return token;
        // }
        // else {
        //     throw new UnauthorizedException('Invalid_token');
        // }

    }

    async generateToken(userId: string): Promise<Token> {

        try {
            const token = await this.findOne({ userId });
            if (token) {
                token.accessToken = uuidv4();
                token.refreshToken = uuidv4();
                token.save();
                return token;
            } else {
                const token = new Token();
                token.userId = userId;
                await token.save();
                return token;
            }

        } catch (error) {
            if (error.code === '23505') {
                //duplicated token
                throw new ConflictException('Token already exists');

            } else {
                throw new InternalServerErrorException();
            }
        }
    }
    async updateToken(accessToken, userId): Promise<any> {
        const token = await this.findOne({ accessToken });
        token.userId = userId;
        token.save();
        return token;
    }
}
