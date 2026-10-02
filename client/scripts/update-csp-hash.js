#!/usr/bin/env node
// Hashes every inline <script> in the BUILT index.html (PostHog snippet plus anything the
// build injects, e.g. the Beasties stylesheet loader) and rewrites the sha256 list in the
// script-src directive of netlify.toml to match. Run after `npm run prod:build`.
// Pass --check to only verify (exit 1 on mismatch) without writing.
const { createHash } = require('node:crypto');
const { existsSync, readFileSync, writeFileSync } = require('node:fs');
const { join } = require('node:path');

const root = join(__dirname, '..');
const check = process.argv.includes('--check');

const indexPath = join(root, 'dist/client/browser/index.html');
if (!existsSync(indexPath)) {
  console.error(`${indexPath} not found -- run \`npm run prod:build\` first`);
  process.exit(1);
}

const indexHtml = readFileSync(indexPath, 'utf8');
const inlineScripts = [...indexHtml.matchAll(/<script(?![^>]*\ssrc=)[^>]*>([\s\S]*?)<\/script>/g)];
if (inlineScripts.length === 0) {
  console.error('No inline <script> found in built index.html');
  process.exit(1);
}

const hashes = inlineScripts.map(
  (m) => `'sha256-${createHash('sha256').update(m[1], 'utf8').digest('base64')}'`,
);

const tomlPath = join(root, 'netlify.toml');
const toml = readFileSync(tomlPath, 'utf8');
const sha256List = /'sha256-[A-Za-z0-9+/=]+'(?: 'sha256-[A-Za-z0-9+/=]+')*/;
if (!sha256List.test(toml)) {
  console.error('No sha256 tokens found in netlify.toml script-src');
  process.exit(1);
}
const updated = toml.replace(sha256List, hashes.join(' '));

if (updated === toml) {
  console.log(`CSP hashes up to date: ${hashes.join(' ')}`);
} else if (check) {
  console.error(`netlify.toml CSP hashes are stale. Expected: ${hashes.join(' ')}`);
  console.error('Run `npm run prod:build && npm run update-csp` and commit netlify.toml.');
  process.exit(1);
} else {
  writeFileSync(tomlPath, updated);
  console.log(`netlify.toml updated with: ${hashes.join(' ')}`);
}
