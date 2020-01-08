import { Component, OnInit, Input } from '@angular/core';
import { Store, select } from '@ngrx/store';
import { State } from 'src/app/core/reducers';
import * as appActions from '../../core/actions/app.actions';
import { Observable, BehaviorSubject, Subject, combineLatest } from 'rxjs';
import { Label, selectLabels, selectBanList } from 'src/app/core/reducers/app.reducer';
import { BanList } from 'src/app/core/models/ban-list.definition';
import { map, withLatestFrom, filter, tap } from 'rxjs/operators';
import { union, difference } from 'lodash';

@Component({
  selector: 'app-ban-lists',
  templateUrl: './ban-lists.component.html',
  styleUrls: ['./ban-lists.component.scss']
})
export class BanListsComponent implements OnInit {
  @Input() token: string;

  labels$: Observable<Label[]>;
  banList$: Observable<BanList>;

  selectedUser$ = new BehaviorSubject<string | undefined>(undefined);
  selectedLabels$ = new BehaviorSubject<Label[]>([]);
  selectedBans$ = new BehaviorSubject<Label[]>([]);

  banAction$ = new Subject();
  unbanAction$ = new Subject();

  users$: Observable<string[]>;
  bans$: Observable<Label[]>;

  constructor(private readonly store: Store<State>) { }

  ngOnInit() {
    this.labels$ = this.store.pipe(select(selectLabels));
    this.banList$ = this.store.pipe(select(selectBanList));
    this.users$ = this.banList$.pipe(
      map(banList => Object.keys(banList))
    );
    this.bans$ = combineLatest(this.selectedUser$.asObservable(), this.banList$).pipe(
      map(([user, banList]) => !!user ? banList[user] : [])
    );

    this.banAction$.asObservable().pipe(
        withLatestFrom(
          this.selectedUser$.asObservable(),
          this.selectedLabels$.asObservable(),
          this.bans$
        ),
        map(([_, selectedUser, selectedLabels, userBans]): [string, Label[], Label[]] => [selectedUser, selectedLabels, userBans]),
        filter(([selectedUser]) => !!selectedUser)
    ).subscribe(([selectedUser, selectedLabels, userBans]) => {
      this.store.dispatch(appActions.updateBanList({
        token: this.token,
        user: selectedUser,
        bans: union(userBans, selectedLabels)
      }));
    });

    this.unbanAction$.asObservable().pipe(
        withLatestFrom(
          this.selectedUser$.asObservable(),
          this.selectedBans$.asObservable(),
          this.bans$
        ),
        map(([_, selectedUser, selectedBans, userBans]): [string, Label[], Label[]] => [selectedUser, selectedBans, userBans]),
        filter(([selectedUser]) => !!selectedUser)
    ).subscribe(([selectedUser, selectedBans, userBans]) => {
      this.store.dispatch(appActions.updateBanList({
        token: this.token,
        user: selectedUser,
        bans: difference(userBans, selectedBans)
      }));
    });

    this.store.dispatch(appActions.requestBanList({ token: this.token }));
    this.store.dispatch(appActions.requestLabels({ token: this.token }));
  }
}
