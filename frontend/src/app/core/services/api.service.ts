import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Label } from '../reducers/app.reducer';
import { sha256 } from 'js-sha256';
import { BanList } from '../models/ban-list.definition';

@Injectable({
    providedIn: 'root'
})
export class ApiService {
    constructor(private httpClient: HttpClient) { }

    login<T = string>(username: string, password: string): Observable<T> {
        let params = new HttpParams();
        params = params.append('username', username);
        params = params.append('password', sha256(password));

        return this.httpClient.get<T>('api/login', { params });
    }

    logout<T = any>(token: string): Observable<T> {
        const params = new HttpParams().set('token', token);

        return this.httpClient.get<T>('api/logout', { params });
    }

    getBanList<T = BanList>(token: string): Observable<T> {
        const params = new HttpParams().set('token', token);

        return this.httpClient.get<T>('api/ban_list', { params });
    }

    getLabels<T = Label[]>(token: string): Observable<T> {
        const params = new HttpParams().set('token', token);

        return this.httpClient.get<T>('api/labels', { params });
    }

    updateBanList<T = Label[]>(token: string, user: string, bans: Label[]): Observable<T> {
        const options: Parameters<HttpClient['post']>[2] = { headers: { 'Content-Type': 'application/json' } };

        return this.httpClient.put<T>('api/ban_list', JSON.stringify({ user, bans, token }), options);
    }
}
