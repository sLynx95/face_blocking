import {
  ActionReducerMap,
  MetaReducer,
} from '@ngrx/store';
import { environment } from '../../../environments/environment';
import * as fromApp from './app.reducer';


export interface State {
  [fromApp.featureKey]: fromApp.AppState;
}


export const reducers: ActionReducerMap<State> = {
  [fromApp.featureKey]: fromApp.reducer,
};


export const metaReducers: MetaReducer<State>[] = !environment.production ? [] : [];
