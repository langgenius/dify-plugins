// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { BaselineControl } from "./types";

export const BASELINE_CONTROLS: BaselineControl[] = [
  { id: "risk-management", article: "Art. 9", name: "Risk Management System", description: "Continuous risk eval flag on agent actions", enforcement: "flag" },
  { id: "data-governance", article: "Art. 10", name: "Data Governance", description: "Training data source logging enabled", enforcement: "logging" },
  { id: "technical-documentation", article: "Art. 11", name: "Technical Documentation", description: "Doc-generation prompt on setup", enforcement: "prompt" },
  { id: "automatic-logging", article: "Art. 12", name: "Automatic Logging", description: "6-month log retention minimum (hard floor)", enforcement: "retention" },
  { id: "transparency", article: "Art. 13", name: "Transparency", description: "AI disclosure on all agent outputs", enforcement: "disclosure" },
  { id: "human-oversight", article: "Art. 14", name: "Human Oversight", description: "Human approval gate (cannot be disabled)", enforcement: "gate" },
  { id: "accuracy-monitoring", article: "Art. 15", name: "Accuracy Monitoring", description: "Performance floor alerts", enforcement: "alert" },
  { id: "quality-management", article: "Art. 17", name: "Quality Management System", description: "Quality management audit trail", enforcement: "audit" },
  { id: "conformity-assessment", article: "Art. 43", name: "Conformity Assessment", description: "Assessment type display", enforcement: "display" },
  { id: "eu-declaration", article: "Art. 47", name: "EU Declaration of Conformity", description: "Declaration upload prompt", enforcement: "prompt" },
  { id: "ce-marking", article: "Art. 48", name: "CE Marking", description: "CE status tracker", enforcement: "tracker" },
  { id: "eu-database", article: "Art. 49", name: "EU Database Registration", description: "Registration check before activation", enforcement: "check" },
  { id: "post-market", article: "Art. 72", name: "Post-Market Monitoring", description: "Post-deployment alert dashboard", enforcement: "dashboard" }
];
