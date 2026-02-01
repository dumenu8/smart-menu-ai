import { Routes } from '@angular/router';

export const routes: Routes = [
    { path: 'admin', loadComponent: () => import('./pages/admin-menu/admin-menu.component').then(m => m.AdminMenuComponent) },
    { path: 'menu', loadComponent: () => import('./pages/customer-menu/customer-menu.component').then(m => m.CustomerMenuComponent) },
    { path: '', redirectTo: 'admin', pathMatch: 'full' },
];
