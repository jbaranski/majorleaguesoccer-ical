---
name: jeff-skill-angular-project
description: Install or update the Angular CLI to the latest version globally. Use when setting up a dev environment, ensuring Angular CLI is current, generating new projects, or when asked to "install Angular", "update Angular", "setup Angular", or "create a new Angular app".
---

## Prerequisites

Before proceeding:

1. Ensure nvm (Node Version Manager) and Node.js are installed using the `jeff-skill-install-nodejs` skill.
2. Use WebSearch to verify current versions:
   - "Angular latest version [current-year]"
   - "Tailwind CSS latest version [current-year]"
   - Update any version references in examples below with verified versions
   - DO NOT skip this step. DO NOT guess at version numbers.

## Steps

1. Run `npm install -g @angular/cli` to install or update to the latest Angular CLI globally.
   - In the update scenario, run `ng update @angular/core @angular/cli` as well
2. Verify installation by running `ng version` and ensure the Angular CLI version is the latest available version.
3. Create a new project by running `ng new <project-name>` and follow the prompts to set up the project with the desired configuration.
   - Use `CSS` for stylesheet format
   - Do NOT enable server side rendering
4. Use the latest stable version of `tailwindcss` as a `devDependency`. Refer to the documentation at https://tailwindcss.com/docs.
   - To install run `ng add tailwindcss` and confirm any prompts. This is equivalent to doing the following (just here for your reference in case something goes wrong or needs to be fixed):
     - `npm install -D tailwindcss @tailwindcss/postcss postcss`
     - Configure `.postcssrc.json` with the following content:

     ```
     {
        "plugins": {
           "@tailwindcss/postcss": {}
        }
     }
     ```

     - `src/styles.css` should contain `@import "tailwindcss"`;

5. Create a `netlify.toml` file in the root of the Angular project directory with the following content:
   ```
    [[redirects]]
      from = "/*"
      to = "/index.html"
      status = 200
   ```

## Integration with Other Skills

- **jeff-skill-error-debugging-rca**: Use when debugging errors or test failures in Angular projects or related tools
- **jeff-skill-angular-aws-cognito**: Integrate AWS Cognito authentication into the Angular app
- **jeff-skill-tailwind-design-system**: Apply Tailwind v4 design tokens, component patterns, and theming after initial project setup

## Additional resources

- Refer to the Angular documentation if you need help: https://angular.io/docs
