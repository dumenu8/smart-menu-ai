import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface MenuItem {
    id?: string;
    name: string;
    description: string;
    price: number;
    image_data?: string;
    category?: string;
    created_at?: string;
}

@Injectable({
    providedIn: 'root'
})
export class MenuService {
    private http = inject(HttpClient);
    private apiUrl = 'http://localhost:8000/menu'; // Assumes local dev for now, can be environment config

    getMenuItems(): Observable<MenuItem[]> {
        return this.http.get<MenuItem[]>(this.apiUrl);
    }

    createMenuItem(item: MenuItem): Observable<MenuItem> {
        return this.http.post<MenuItem>(this.apiUrl, item);
    }

    deleteMenuItem(id: string): Observable<any> {
        return this.http.delete(`${this.apiUrl}/${id}`);
    }

    updateMenuItem(id: string, item: any): Observable<MenuItem> {
        return this.http.put<MenuItem>(`${this.apiUrl}/${id}`, item);
    }
}
