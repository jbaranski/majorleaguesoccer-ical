import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';
import posthog from 'posthog-js';
import { environment } from './environments/environment';

posthog.init(environment.posthogKey, {
  api_host: environment.posthogHost,
  defaults: '2026-01-30',
});

bootstrapApplication(AppComponent, appConfig).catch((err) => console.error(err));
