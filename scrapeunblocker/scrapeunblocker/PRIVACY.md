# Privacy Policy

This plugin sends data to the ScrapeUnblocker API (`https://api.scrapeunblocker.com`),
a third-party service operated by ScrapeUnblocker. Please read this before installing.

## What leaves your Dify instance

**Get Page Source**

- The **target URL** you ask the plugin to fetch, including any query string it contains.
- The optional `proxy_country` value.

The page is then fetched by ScrapeUnblocker's infrastructure, not by your Dify
instance. This means the **content of the target page passes through
ScrapeUnblocker's servers** before it reaches you, and the target website sees a
request from a ScrapeUnblocker IP address rather than from you.

**Search Google**

- The **search keyword** you provide, plus the optional `pages_to_check` and
  `proxy_country` values.

**Both tools**

- Your ScrapeUnblocker API key, sent as the `X-ScrapeUnblocker-Key` request header.

## What is not sent

The plugin sends only the parameters listed above. It does not read or transmit
your Dify workspace data, conversation history, other credentials, or files.

## Storage

This plugin stores nothing itself. Your API key is held by Dify in its credential
store and is used only to authenticate requests to ScrapeUnblocker. The API key is
never written to logs and is never included in error messages returned by the plugin.

Requests you make are subject to ScrapeUnblocker's own retention and logging
practices as the operator of that API.

## Things to be aware of

- **Do not put sensitive data in target URLs.** Anything in the URL, including
  tokens or identifiers in the query string, is transmitted to ScrapeUnblocker.
- **URLs are fetched as given.** The plugin does not restrict which hosts can be
  requested; the request is made by ScrapeUnblocker's infrastructure, from its
  network, not from your Dify host.
- Fetching a page may be subject to that website's terms of service. You are
  responsible for ensuring your use is lawful and permitted.

## Contact and further information

- Website: https://www.scrapeunblocker.com
- Documentation: https://developers.scrapeunblocker.com

For details on how ScrapeUnblocker handles data as a service provider, see the
privacy policy published on its website.
