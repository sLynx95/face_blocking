import { createReducer, Action, on, createSelector } from '@ngrx/store';
import { State } from '.';
import * as appActions from '../actions/app.actions';
import { BanList } from '../models/ban-list.definition';

export const featureKey = 'App';

export type Label = string;
export interface LoginData {
  username: string;
  token: string;
}

// State
export interface AppState {
  loginData?: LoginData;
  loggedState: 'loggedOut' | 'loggingIn' | 'loggedIn' | 'wrongCredentials';
  banList: BanList;
  labels: Label[];
}

export const initialState: AppState = {
  loggedState: 'loggedOut',
  banList: {},
  labels: []
};

// Reducer
const appReducer = createReducer<AppState>(initialState,
  on(appActions.login, state => ({...state, loggedState: 'loggingIn' })),
  on(appActions.successfulLogin, (state, { loginData }) => ({...state, loggedState: 'loggedIn', loginData })),
  on(appActions.failedLogin, state => ({...state, loggedState: 'wrongCredentials' })),
  on(appActions.logout, state => ({...state, loggedState: 'loggedOut', loginData: undefined })),
  on(appActions.loadBanList, (state, { banList }) => ({...state, banList })),
  on(appActions.loadLabels, (state, { labels }) => ({...state, labels })),
);

export function reducer(state: AppState | undefined, action: Action) {
  return appReducer(state, action);
}

// Selectors
export const selectAppState = (state: State) => state[featureKey];
export const selectLoggedState = createSelector(selectAppState, state => state.loggedState);
export const selectToken = createSelector(selectAppState, (state): string => state.loginData ? state.loginData.token : '');
export const selectBanList = createSelector(selectAppState, state => state.banList);
export const selectLabels = createSelector(selectAppState, state => state.labels);
export const selectLoggedInUserName = createSelector(selectAppState, (state): string => state.loginData ? state.loginData.username : '');
