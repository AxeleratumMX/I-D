import { IsNotEmpty, IsUUID, IsOptional } from 'class-validator';

export class FilterDto {

    @IsNotEmpty()
    @IsUUID()
    readonly userId: string;

    @IsNotEmpty()
    @IsUUID()
    readonly resourceId: string;

    @IsOptional()
    @IsNotEmpty()
    @IsUUID()
    readonly frameId: string;
}
