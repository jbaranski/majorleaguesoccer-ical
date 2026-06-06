import { Injectable } from '@angular/core';
import posthog from 'posthog-js';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class PosthogService {
  constructor() {
    posthog.init(environment.posthogKey, {
      api_host: environment.posthogHost,
      person_profiles: 'identified_only'
    });
  }

  capture(event: string, properties?: Record<string, unknown>): void {
    posthog.capture(event, properties);
  }
}
