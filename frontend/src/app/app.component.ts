import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { AppState, selectLoggedState, selectToken, selectLoggedInUserName } from './core/reducers/app.reducer';
import { Store, select } from '@ngrx/store';
import { State } from './core/reducers';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  loggedState$: Observable<AppState['loggedState']>;
  token$: Observable<string>;
  username$: Observable<string>;

  constructor(private readonly store: Store<State>) { }

  ngOnInit() {
    this.loggedState$ = this.store.pipe(select(selectLoggedState));
    this.token$ = this.store.pipe(select(selectToken));
    this.username$ = this.store.pipe(select(selectLoggedInUserName));
  }
}
