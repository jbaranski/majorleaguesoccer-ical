const { writeFileSync, mkdirSync } = require('fs');

const key = process.env.POSTHOG_KEY;
const host = process.env.POSTHOG_HOST ?? 'https://us.i.posthog.com';

if (!key) {
  console.error('Error: POSTHOG_KEY environment variable is not set. Aborting build.');
  process.exit(1);
}

mkdirSync('./src/environments', { recursive: true });

writeFileSync(
  './src/environments/environment.ts',
  `export const environment = {
  production: true,
  posthogKey: '${key}',
  posthogHost: '${host}'
};
`
);

console.log('Generated src/environments/environment.ts');
