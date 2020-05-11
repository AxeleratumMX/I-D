import { EntityRepository, Repository, In } from 'typeorm';
import { ApiScope } from '../entity/apiScope.entity';
import { ApplicationApiScope } from '../entity/application-apiScope.entity';

@EntityRepository(ApiScope)
export class ApiScopeRepository extends Repository<ApiScope> {
    async getApiScopesByApplicatiopn(apiScopeIds: number[]): Promise<string[]> {
        const apiScopes = await this.find({ where: { apiScopeId: In([apiScopeIds]) } });
        let validApiScopes: string[];
        apiScopes.forEach(element => {
            validApiScopes.push(element.modifier);
        });
        return validApiScopes;
    }

}
