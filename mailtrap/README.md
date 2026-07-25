# Mailtrap Plugin for Dify

Send transactional emails, test in sandbox, and manage email infrastructure via [Mailtrap's Email API](https://mailtrap.io).

## Features

- Send transactional and bulk emails via Mailtrap Email API
- Test emails safely in Mailtrap Sandbox without delivering to real inboxes
- Manage sending domains, contacts, and email templates
- Check delivery logs and sending statistics

## Setup

1. Sign up at [mailtrap.io](https://mailtrap.io/signup)
2. Get your API token from [API settings](https://mailtrap.io/api-tokens)
3. Get your Account ID from [account management](https://mailtrap.io/account-management)
4. In Dify, install this plugin and enter your credentials:
   - **API Token**: Your Mailtrap API token
   - **Account ID**: Your Mailtrap account ID

## Usage

### Send Email
Sends a transactional email via Mailtrap Email API.

**Parameters:**
- `to_email` (required): Recipient email address
- `subject` (required): Email subject
- `body` (required): Email body (HTML or plain text)
- `from_email` (optional): Sender email (must be from a verified domain)
- `sandbox` (optional): Set to true to send to Mailtrap Sandbox for testing

## Requirements

- A Mailtrap account
- A verified sending domain (for production sending)
- Mailtrap API token

## Source Repository

https://github.com/mailtrap/mailtrap-mcp

## Privacy Policy

See [PRIVACY.md](PRIVACY.md)
