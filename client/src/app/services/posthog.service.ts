import { Injectable } from '@angular/core';
import posthog from 'posthog-js';

@Injectable({
  providedIn: 'root'
})
export class PosthogService {
  capture(event: string, properties?: Record<string, unknown>): void {
    posthog.capture(event, properties);
  }
}
