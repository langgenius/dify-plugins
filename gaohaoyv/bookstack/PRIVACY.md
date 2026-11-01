# Privacy Policy

This plugin uses credentials supplied by the user through the Dify provider form and connects only to the configured BookStack instance through the Dify runtime operated by the user.

## Data Handling

- The plugin may read BookStack books, chapters, and pages, may search pages, and may create or update BookStack pages only when the user invokes the corresponding tools.
- The plugin does not persist BookStack credentials.
- The plugin does not log `token_secret` values.
- The plugin does not send data to third parties beyond the configured BookStack instance and the Dify runtime that executes the plugin.

## Redaction Guidance

When documenting or capturing screenshots, redact:

- real BookStack hosts or URLs
- real token values
- raw `Authorization` headers
- user names
- internal project names
- production page URLs or identifiers

## Scope Note

This policy describes the current Tool plugin privacy baseline. It does not cover future Datasource packaging or any separate submission track unless that work is explicitly brought into scope.
