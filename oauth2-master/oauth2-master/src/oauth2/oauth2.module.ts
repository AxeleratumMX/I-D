import { Module, HttpModule, MiddlewareConsumer, RequestMethod } from '@nestjs/common';
import { Oauth2Controller } from './oauth2.controller';
import { Oauth2Service } from './oauth2.service';
import { PassportModule } from '@nestjs/passport';
import { JwtModule } from '@nestjs/jwt';
import { JwtStrategy } from './jwt.strategy';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ApiScopeRepository } from './repository/apiScope.repository';
import { ApplicationApiScopeRepository } from './repository/application-apiscope.repository';
import { ApplicationRepository } from './repository/application.repository';
import { AuthorizedRepository } from './repository/authorized.repository';
import { ConnotationRepository } from './repository/connotation.repository';
import { TokenRepository } from './repository/token.repository';
import { UserApplicationRepository } from './repository/user-application.repository';
import { UserRepository } from './repository/user.repository';
import { AuthorizationRepository } from './repository/authorization.repository';
import { CompanyRepository } from './repository/company.repository';
import { PermissionRepository } from './repository/permission.repository';
import { UserCompanyRepository } from './repository/user-company.repository';
import { UserWorkspaceRepository } from './repository/user-workspace.repository';
import { WorkspaceRepository } from './repository/workspace.repository';
import { jwtConstants } from './jwt-constants';
import { AuthorizeMiddleware } from './authorize.middleware';
import { RefreshMiddleware } from './refresh.middleware';

@Module({
  imports: [
    HttpModule,
    PassportModule.register({ defaultStrategy: 'jwt' }),
    JwtModule.register({
      privateKey: jwtConstants.privateKey,
      publicKey: jwtConstants.publicKey,
      signOptions: {
        algorithm: 'RS256',
        issuer: 'vili.tech',
      },
    }),
    TypeOrmModule.forFeature([
      ApiScopeRepository,
      ApplicationApiScopeRepository,
      ApplicationRepository,
      AuthorizationRepository,
      AuthorizedRepository,
      CompanyRepository,
      ConnotationRepository,
      PermissionRepository,
      TokenRepository,
      UserApplicationRepository,
      UserCompanyRepository,
      UserWorkspaceRepository,
      UserRepository,
      WorkspaceRepository,
    ]),
  ],
  controllers: [Oauth2Controller],
  providers: [
    Oauth2Service,
    JwtStrategy,
  ],
  exports: [
    JwtStrategy,
    PassportModule,
  ],
})
export class Oauth2Module {
  configure(consumer: MiddlewareConsumer) {
    consumer
      .apply(AuthorizeMiddleware)
      .forRoutes({ path: 'v0/oauth2/authorize', method: RequestMethod.GET });
    consumer
      .apply(RefreshMiddleware)
      .forRoutes({ path: 'v0/oauth2/token', method: RequestMethod.POST });
  }


}
