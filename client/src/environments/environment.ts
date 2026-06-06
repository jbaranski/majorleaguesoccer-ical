// This file is overwritten at Netlify build time by scripts/set-env.js
// which reads POSTHOG_KEY and POSTHOG_HOST from Netlify environment variables.
export const environment = {
  production: true,
  posthogKey: '',
  posthogHost: 'https://us.i.posthog.com'
};
