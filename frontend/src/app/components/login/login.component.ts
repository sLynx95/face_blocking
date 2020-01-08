import { Component, OnInit } from '@angular/core';
import { State } from 'src/app/core/reducers';
import { Store, select } from '@ngrx/store';
import { login } from 'src/app/core/actions/app.actions';
import { AppState, selectLoggedState } from 'src/app/core/reducers/app.reducer';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {
  username = '';
  password = '';
  loggedState$: Observable<AppState['loggedState']>;

  constructor(private readonly store: Store<State>) { }

  ngOnInit() {
    this.loggedState$ = this.store.pipe(
      select(selectLoggedState)
    );
  }

  login() {
    this.store.dispatch(login({ username: this.username, password: this.password }));
  }
}
