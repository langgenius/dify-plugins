# Privacy Policy — HOL Guard Dify plugin

This plugin performs command-risk inspection locally inside the Dify plugin runtime using HOL Guard's side-effect-free command inspection API.

- The command text provided to the tool is analyzed locally.
- This plugin does not execute the inspected command.
- This plugin does not store command text or send it to HOL, Dify, or another third party.
- No credentials are required.
- The plugin does not make network requests during command inspection.

Dify itself may retain workflow inputs or outputs according to the operator's Dify configuration and policies. That behavior is outside this plugin.
