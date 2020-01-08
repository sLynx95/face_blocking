import { Label } from '../reducers/app.reducer';

export interface BanList {
    [username: string]: Label[];
}
