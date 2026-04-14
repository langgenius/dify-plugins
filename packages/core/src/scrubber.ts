// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

/**
 * Universal scrubber for PII and Secrets in agent tool calls.
 * Used to protect data before it is sent to 3rd-party semantic analysis LLMs.
 */
export function scrubPayload(payload: any, additionalSecrets: string[] = []): any {
    if (!payload) return payload;

    let payloadString = typeof payload === "string" ? payload : JSON.stringify(payload);

    // 1. Redact known secrets
    for (const secret of additionalSecrets) {
        if (!secret) continue;
        payloadString = payloadString.split(secret).join("[REDACTED_SECRET]");
    }

    // 2. PHI / PII Patterns (HIPAA & GDPR article 17 compliance)
    const PII_PATTERNS = [
        { pattern: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g, label: "EMAIL" },
        { pattern: /\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b/g, label: "PHONE" },
        { pattern: /\b\d{3}-\d{2}-\d{4}\b/g, label: "SSN" },
        { pattern: /\b(?:\d{1,3}\.){3}\d{1,3}\b/g, label: "IP_V4" },
        { pattern: /\b\d{2}[/-]\d{2}[/-]\d{4}\b/g, label: "DATE" },
        { pattern: /\b\d{4}[/-]\d{2}[/-]\d{2}\b/g, label: "DATE_ISO" },
        { pattern: /\bsw_[a-zA-Z0-9]{32,}\b/g, label: "SW_API_KEY" }, // Specific SupraWall keys
        { pattern: /\b(sk-[a-zA-Z0-9]{20,})\b/g, label: "OPENAI_KEY" },
    ];

    for (const { pattern, label } of PII_PATTERNS) {
        payloadString = payloadString.replace(pattern, `[REDACTED_${label}]`);
    }

    if (typeof payload === "string") return payloadString;
    try {
        return JSON.parse(payloadString);
    } catch {
        return payloadString;
    }
}
