// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

/**
 * MailerLite Transactional Email Client for SupraWall.
 * Handles delivery of security alerts, HITL approvals, and system notifications.
 */

const MAILERLITE_API_URL = 'https://connect.mailerlite.com/api';

export interface MailerLiteEmailOptions {
  to: {
    email: string;
    name?: string;
  };
  from: {
    email: string;
    name?: string;
  };
  subject: string;
  html: string;
  variables?: Record<string, any>;
}

export async function sendTransactionalEmail(options: MailerLiteEmailOptions) {
  const apiKey = process.env.MAILERLITE_API_KEY;

  if (!apiKey) {
    throw new Error('MAILERLITE_API_KEY is not defined in environment variables');
  }

  try {
    const response = await fetch(`${MAILERLITE_API_URL}/emails/transactional`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        subject: options.subject,
        from: options.from,
        to: options.to,
        html: options.html,
        variables: options.variables
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      console.error('MailerLite API error (POST transactional):', data);
      throw new Error(data.message || 'Failed to send transactional email via MailerLite');
    }

    return { success: true, data };
  } catch (error) {
    console.error('MailerLite send error:', error);
    return { success: false, error };
  }
}
