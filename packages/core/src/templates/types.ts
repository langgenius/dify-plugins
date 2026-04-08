// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

export interface BaselineControl {
  id: string;
  article: string;
  name: string;
  description: string;
  enforcement: string;
}

export interface SectorOverride {
  id: string;
  name: string;
  description: string;
  enforcement: string;
}

export interface PolicyRule {
  toolname: string;
  ruletype: "ALLOW" | "DENY" | "REQUIRE_APPROVAL";
  condition?: string;
  priority?: number;
  description: string;
}

export interface SectorTemplate {
  id: string;                          // e.g., "hr-employment"
  annexCategory: number;               // 1–8
  name: string;
  description: string;
  complianceDeadline: string;          // ISO date
  conformityAssessment: "self" | "third-party";
  version: string;                     // e.g., "1.0.0"
  baselineControls: BaselineControl[]; // Shared controls (always ON)
  sectorOverrides: SectorOverride[];   // Unique per template
  policyRules: PolicyRule[];           // Auto-generated policy rules
  riskLevel: "high" | "critical";
}
