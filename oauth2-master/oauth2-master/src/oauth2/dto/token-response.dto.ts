export class TokenResponse {
    // tslint:disable-next-line: variable-name
    id_token?: string;
    // tslint:disable-next-line: variable-name
    access_token: string;
    // tslint:disable-next-line: variable-name
    token_type: string;
    // tslint:disable-next-line: variable-name
    expires_in: string;
    // tslint:disable-next-line: variable-name
    refresh_token: string;
    scope: string[];
}
