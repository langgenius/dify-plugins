# Privacy Policy

This plugin lets users search remote job listings through the public APIs of
two third-party services:

- **Jobicy** (`https://jobicy.com/api/v2/remote-jobs`)
- **Remotive** (`https://remotive.com/api/remote-jobs`)

## What data is sent

When you invoke the `search_jobs` tool, the plugin sends only:

- The search keyword, category, location, job type, and result count that you
  provide, to the selected job board API over HTTPS.

No API keys or credentials are collected, stored, or transmitted by this
plugin, because the underlying job board APIs are public and do not require
authentication.

## What data is stored

This plugin stores **no user data**. It does not keep logs, cookies, or any
local state. Search requests are made on demand and discarded after the
response is returned.

## What data is shared

Search queries are forwarded to the selected third-party API (Jobicy or
Remotive) so that it can return matching job listings. The plugin does not
share data with any other party, and it does not send user content anywhere
except to the selected job board API.

## Third-party policies

Please review the privacy policies of the job board services for their own
data handling practices:

- Jobicy: <https://jobicy.com/>
- Remotive: <https://remotive.com/>
