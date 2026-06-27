import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: 'international',
    loadComponent: () => import('./international/international.component').then((m) => m.InternationalComponent)
  }
];
