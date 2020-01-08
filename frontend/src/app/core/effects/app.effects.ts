import { Injectable } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { ApiService } from '../services/api.service';
import { switchMap, map, catchError } from 'rxjs/operators';
import * as appActions from '../actions/app.actions';
import { of, EMPTY } from 'rxjs';

@Injectable()
export class AppEffects {
  constructor(
    private actions$: Actions,
    private apiService: ApiService,
  ) { }

  login$ = createEffect(() => this.actions$.pipe(
    ofType(appActions.login),
    switchMap(({ username, password }) => this.apiService.login(username, password).pipe(
      map(token => appActions.successfulLogin({ loginData: { token, username } })),
      catchError(() => of(appActions.failedLogin()))
    ))
  ));

  logout$ = createEffect(() => this.actions$.pipe(
    ofType(appActions.logout),
    switchMap(({ token }) => this.apiService.logout(token).pipe(
      catchError(() => EMPTY)
    ))
  ), { dispatch: false });

  requestBanList$ = createEffect(() => this.actions$.pipe(
    ofType(appActions.requestBanList),
    switchMap(({ token }) => this.apiService.getBanList(token).pipe(
      map(banList => appActions.loadBanList({ banList })),
      catchError(() => EMPTY)
    ))
  ));

  requestLabels$ = createEffect(() => this.actions$.pipe(
    ofType(appActions.requestLabels),
    switchMap(({ token }) => this.apiService.getLabels(token).pipe(
      map(labels => appActions.loadLabels({ labels })),
      catchError(() => EMPTY)
    ))
  ));

  updateBanList$ = createEffect(() => this.actions$.pipe(
    ofType(appActions.updateBanList),
    switchMap(({ token, user, bans }) => this.apiService.updateBanList(token, user, bans).pipe(
      map(() => appActions.requestBanList({ token })),
      catchError(() => EMPTY)
    ))
  ));
}
