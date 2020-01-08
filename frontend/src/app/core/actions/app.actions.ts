import { createAction, props } from '@ngrx/store';
import { LoginData, Label } from '../reducers/app.reducer';
import { BanList } from '../models/ban-list.definition';

const prefix = '[App]';

interface Token {
    token: string;
}

export const login = createAction(`${prefix} Login`, props<{ username: string, password: string }>());
export const failedLogin = createAction(`${prefix} Failed login`);
export const successfulLogin = createAction(`${prefix} Successful login`, props<{ loginData: LoginData }>());
export const logout = createAction(`${prefix} Logout`, props<Token>());

export const requestBanList = createAction(`${prefix} Request ban list`, props<Token>());
export const requestLabels = createAction(`${prefix} Request labels`, props<Token>());
export const updateBanList = createAction(`${prefix} Update ban list`, props<Token & { user: string, bans: Label[] }>());

export const loadBanList = createAction(`${prefix} Load ban list`, props<{ banList: BanList }>());
export const loadLabels =  createAction(`${prefix} Load labels`, props<{ labels: Label[] }>());
