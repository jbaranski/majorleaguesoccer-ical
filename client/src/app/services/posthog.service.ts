import { Injectable } from '@angular/core';

declare global {
  interface Window {
    posthog?: { capture: (event: string, properties?: Record<string, unknown>) => void };
  }
}

@Injectable({ providedIn: 'root' })
export class PosthogService {
  capture(event: string, properties?: Record<string, unknown>): void {
    window.posthog?.capture(event, properties);
  }
}
