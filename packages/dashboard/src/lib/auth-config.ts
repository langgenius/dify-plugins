// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

export type AuthMode = "stealth" | "open";

export function getAuthMode(): AuthMode {
  const mode = process.env.NEXT_PUBLIC_AUTH_MODE?.toLowerCase();
  if (mode === "open") return "open";
  return "stealth";
}

export function getAdminEmails(): string[] {
  // Use NEXT_PUBLIC_ for client-side visibility
  const raw = process.env.NEXT_PUBLIC_ADMIN_EMAILS || process.env.ADMIN_EMAILS || "";
  const emails = raw.split(",").map(e => e.trim()).filter(Boolean);
  
  // Emergency fallback for owner access in private repo
  if (emails.length === 0) {
    return ["peghin@gmail.com"];
  }
  return emails;
}

export function isAdminEmail(email: string | null | undefined): boolean {
  if (!email) return false;
  const admins = getAdminEmails();
  return admins.includes(email);
}

export function isRegistrationEnabled(): boolean {
  return getAuthMode() === "open";
}
