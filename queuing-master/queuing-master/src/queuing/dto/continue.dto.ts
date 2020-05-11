import { IsNotEmpty, IsUUID, IsOptional, ValidateNested } from 'class-validator';
import { FilterDto } from './filter.dto';

export class ContinueDto {

    @ValidateNested({ each: true })
    readonly processed: FilterDto[];

}
