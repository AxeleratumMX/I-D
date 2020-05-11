import { EntityRepository, Repository, QueryFailedError } from 'typeorm';
import * as bcrypt from "bcrypt";
import { User } from '../entity/user.entity';
import { AuthorizationRequest } from '../dto/authorization-request.dto';
import { AuthenticationRequest } from '../dto/authentication-request.dto';
import { ConflictException, InternalServerErrorException, UnauthorizedException, Logger } from '@nestjs/common';
import { RegistrationRequest } from '../dto/registration-request.dto';
import * as uuidv4 from 'uuid/v4';
import { TokenRequest } from '../dto/token-request.dto';

@EntityRepository(User)
export class UserRepository extends Repository<User> {

    async validateUserPassword(tokenRequest: TokenRequest): Promise<string> {
        const { username: email, password } = tokenRequest;
        const user = await this.findOne({ email });
        if (user) {
            try {
                const validPassword = await bcrypt.compare(password, user.password);
                if (!validPassword) {
                    throw new UnauthorizedException('Invalid Credentials');
                }
                return user.id;
            } catch (error) {
                if (error instanceof QueryFailedError) {
                    throw new InternalServerErrorException(error);
                } else {
                    throw error;
                }
            }
        } else {
            throw new UnauthorizedException('Invalid Credentials');
        }
    }
}
