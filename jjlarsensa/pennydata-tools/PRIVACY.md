# Privacy Policy: PennyData Tools (Dify plugin)

**This plugin does not collect, store, or log any user data, and the plugin author receives none.**

What happens when you use it:

- You supply your own Apify API token as a credential. Dify stores it as a secret; the plugin sends it only to `api.apify.com` in an `Authorization` header to start a run and return its results.
- The input you give a tool (URLs, email addresses, or domain names) is sent to the Apify API (`https://api.apify.com/v2/acts/pennydata~<actor>/run-sync-get-dataset-items`) and processed by the public PennyData actor on Apify's platform. Apify handles that data under its own terms and privacy policy (https://apify.com/privacy-policy), and your Apify account keeps the run history and dataset.
- The actors fetch the websites you list, look up public DNS and RDAP/WHOIS records, and check email addresses by syntax, DNS and public lists only. They do not contact mailboxes.
- The plugin has no server, database, analytics, telemetry, or logging of its own. Nothing is sent to the plugin author or to any party other than Apify.

Email addresses are personal data under GDPR when they identify a person. You decide which addresses you submit; make sure you have a lawful basis to process them.

Contact: open an issue at https://github.com/jjlarsensa/bulk-whois-dns-api/issues
