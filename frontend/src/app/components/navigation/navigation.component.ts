import { Component, OnInit, Input } from '@angular/core';
import { Store } from '@ngrx/store';
import { State } from 'src/app/core/reducers';
import * as appActions from '../../core/actions/app.actions';

@Component({
  selector: 'app-navigation',
  templateUrl: './navigation.component.html',
  styleUrls: ['./navigation.component.scss']
})
export class NavigationComponent implements OnInit {
  @Input() token: string;
  @Input() username: string;

  constructor(private readonly store: Store<State>) { }

  ngOnInit() { }

  logout() {
    this.store.dispatch(appActions.logout({ token: this.token }));
  }
}
