import { EntityRepository, Repository } from 'typeorm';
import { ApplicationApiScope } from '../entity/application-apiScope.entity';
import { TokenRequest } from '../dto/token-request.dto';
import { UnauthorizedException } from '@nestjs/common';
import { IsNotEmpty } from 'class-validator';

@EntityRepository(ApplicationApiScope)
export class ApplicationApiScopeRepository extends Repository<ApplicationApiScope> {
    async getApplicationApiScopes(tokenRequest: TokenRequest): Promise<number[]> {
        // console.log('hola');

        // tslint:disable-next-line: variable-name
        const { client_id: applicationId } = tokenRequest;
        const applicationApiScopes = await this.find({ applicationId });
        // tslint:disable-next-line: prefer-const
        if (applicationApiScopes) {
            let apiScopes: number[];
            console.log('here1');
            applicationApiScopes.forEach(element => {
                console.log('here2');

                apiScopes.push(element.apiScopeId);
            });
            console.log(applicationApiScopes);

            return apiScopes;
        } else {
            throw new UnauthorizedException('No associated scopes');
        }
    }
}
