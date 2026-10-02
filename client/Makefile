.PHONY: all build test lint deploy

all: lint test build

lint:
	npm run prettier:check

test:
	npx ng test --watch=false --browsers=ChromeHeadlessNoSandbox

# update-csp hashes the inline scripts in the built index.html, so it must run after the build.
build:
	npm run prod:build
	npm run update-csp

# netlify-cli is NOT added as a devDependency -- npx downloads it at deploy time.
deploy: build
	npx netlify-cli deploy --prod --dir=dist/client/browser
