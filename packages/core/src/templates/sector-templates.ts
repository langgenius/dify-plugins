// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { SectorTemplate } from "./types";
import { BASELINE_CONTROLS } from "./baseline-controls";

export const SECTOR_TEMPLATES: SectorTemplate[] = [
  {
    id: "biometrics",
    annexCategory: 1,
    name: "Biometrics",
    description: "Biometric identification and categorisation systems.",
    complianceDeadline: "2026-08-02",
    conformityAssessment: "third-party",
    riskLevel: "critical",
    version: "1.0.0",
    baselineControls: BASELINE_CONTROLS,
    sectorOverrides: [
      { id: "block-real-time-id", name: "Block real-time ID in public spaces", description: "Blocks agent from parsing live video for ID", enforcement: "DENY" },
      { id: "emotion-limiter", name: "Emotion-recognition scope limiter", description: "Flags emotional analysis queries", enforcement: "REQUIRE_APPROVAL" },
      { id: "third-party-lock", name: "Third-party lock", description: "Requires external auditor sign-off", enforcement: "flag" },
      { id: "per-event-logger", name: "Per-event logger", description: "Extreme audit granularity", enforcement: "logging" }
    ],
    policyRules: [
      { toolname: "video_analysis", ruletype: "DENY", condition: "action == 'real_time_id' && context == 'public'", description: "Block real-time ID in public spaces" },
      { toolname: "facial_analysis", ruletype: "REQUIRE_APPROVAL", condition: "action == 'emotion_recognition'", description: "Emotion-recognition requires approval" }
    ]
  },
  {
    id: "critical-infrastructure",
    annexCategory: 2,
    name: "Critical Infrastructure",
    description: "Management and operation of critical infrastructure.",
    complianceDeadline: "2026-08-02",
    conformityAssessment: "self",
    riskLevel: "critical",
    version: "1.0.0",
    baselineControls: BASELINE_CONTROLS,
    sectorOverrides: [
      { id: "hard-kills-switch", name: "Hard failsafe kill switch", description: "Instant agent termination API enabled", enforcement: "flag" },
      { id: "human-physical-confirm", name: "Mandatory human confirm before physical action", description: "All hardware APIs require approval", enforcement: "REQUIRE_APPROVAL" },
      { id: "real-time-logging", name: "Real-time continuous logging", description: "No buffered logs", enforcement: "logging" },
      { id: "disconnection-safety", name: "Disconnection safety mode", description: "Fails safe on network loss", enforcement: "flag" }
    ],
    policyRules: [
      { toolname: "scada_control", ruletype: "REQUIRE_APPROVAL", description: "Mandatory human confirm before physical action" },
      { toolname: "hardware_api", ruletype: "REQUIRE_APPROVAL", description: "Mandatory human confirm before physical action" }
    ]
  },
  {
    id: "education",
    annexCategory: 3,
    name: "Education",
    description: "Education and vocational training.",
    complianceDeadline: "2026-08-02",
    conformityAssessment: "self",
    riskLevel: "high",
    version: "1.0.0",
    baselineControls: BASELINE_CONTROLS,
    sectorOverrides: [
      { id: "block-autonomous-grading", name: "Block autonomous deny/grant", description: "No automated admission rejections without human", enforcement: "DENY" },
      { id: "scoring-explainability", name: "Explainability on all scoring", description: "Must generate reasoning for any score", enforcement: "flag" },
      { id: "behavioral-review", name: "Human review before behavioral action", description: "Proctoring flags require review", enforcement: "REQUIRE_APPROVAL" }
    ],
    policyRules: [
      { toolname: "admission_decision", ruletype: "REQUIRE_APPROVAL", condition: "decision == 'reject'", description: "Block autonomous deny" },
      { toolname: "student_scoring", ruletype: "ALLOW", description: "Must generate reasoning for any score (enforced in prompt)" }
    ]
  },
  {
    id: "hr-employment",
    annexCategory: 4,
    name: "HR & Employment",
    description: "Employment, workers management and access to self-employment.",
    complianceDeadline: "2026-08-02",
    conformityAssessment: "self",
    riskLevel: "high",
    version: "1.0.0",
    baselineControls: BASELINE_CONTROLS,
    sectorOverrides: [
      { id: "bias-audit-trail", name: "Bias audit trail", description: "Records demographic signals for disparity testing", enforcement: "logging" },
      { id: "block-autonomous-hire-fire", name: "Block autonomous hire/fire", description: "Cannot execute termination or offer without human", enforcement: "DENY" },
      { id: "emp-notification", name: "Employee notification", description: "Flags when to notify employee of AI decision", enforcement: "flag" },
      { id: "gdpr-dpia-trigger", name: "GDPR DPIA trigger", description: "Links to GDPR DPIA records", enforcement: "flag" }
    ],
    policyRules: [
      { toolname: "termination_api", ruletype: "DENY", description: "EU AI Act Art 14: Automated employee termination is blocked" },
      { toolname: "*", ruletype: "REQUIRE_APPROVAL", condition: "(hire|reject|shortlist).*(candidate|applicant|employee)", description: "Hiring and rejection decisions require human sign-off" },
      { toolname: "*", ruletype: "REQUIRE_APPROVAL", condition: "(salary|compensation|bonus|pay.?rise|pay.?increase)", description: "Compensation changes require HR manager approval" },
      { toolname: "*", ruletype: "REQUIRE_APPROVAL", condition: "(performance.review|appraisal|evaluation).*(submit|publish|final)", description: "Performance evaluations must be reviewed before publishing" },
      { toolname: "database", ruletype: "DENY", condition: "bulk.*(export|download).*(employ|staff|personnel|hr)", description: "Prevent bulk export of HR and employee personal data" }
    ]
  },
  {
    id: "healthcare",
    annexCategory: 5,
    name: "Healthcare",
    description: "Access to and enjoyment of essential private services and public services and benefits.",
    complianceDeadline: "2026-08-02",
    conformityAssessment: "third-party",
    riskLevel: "critical",
    version: "1.0.0",
    baselineControls: BASELINE_CONTROLS,
    sectorOverrides: [
      { id: "phi-data-gov", name: "PHI data governance", description: "Strict anonymization of patient data in logs", enforcement: "logging" },
      { id: "breach-notification", name: "Breach notification workflow", description: "72-hour trigger", enforcement: "flag" },
      { id: "ce-device-path", name: "CE marking for device path", description: "Specific docs required", enforcement: "flag" }
    ],
    policyRules: [
      { toolname: "triage_decision", ruletype: "REQUIRE_APPROVAL", description: "Human in the loop for triage" },
      { toolname: "benefit_denial", ruletype: "DENY", description: "Cannot autonomously deny health benefits" },
      { toolname: "*", ruletype: "REQUIRE_APPROVAL", condition: "(patient|ehr|medical.record|health.record).*(write|update|modify|create)", description: "Medical record modifications require clinician approval" },
      { toolname: "*", ruletype: "REQUIRE_APPROVAL", condition: "(dosage|prescription|medic[ai]tion|drug.order)", description: "Medication and prescription actions require physician sign-off" },
      { toolname: "*", ruletype: "REQUIRE_APPROVAL", condition: "(diagnos(is|e|es|ing)|treatment[._-]?plan|clinical[._-]?decision|clinical[._-]?recommendation)", description: "Clinical decisions must be reviewed by a qualified professional" },
      { toolname: "*", ruletype: "DENY", condition: "(send|share|transmit|export).*patient", description: "Block unauthorised sharing of patient data" }
    ]
  },
  {
    id: "law-enforcement",
    annexCategory: 6,
    name: "Law Enforcement",
    description: "Law enforcement.",
    complianceDeadline: "2026-08-02",
    conformityAssessment: "third-party",
    riskLevel: "critical",
    version: "1.0.0",
    baselineControls: BASELINE_CONTROLS,
    sectorOverrides: [
      { id: "profiling-blocker", name: "Profiling blocker", description: "No predictive policing based solely on demographics", enforcement: "DENY" },
      { id: "probabilistic-labeling", name: "Probabilistic labeling on recidivism", description: "Forces confidence scores on outputs", enforcement: "flag" },
      { id: "block-action-from-profile", name: "Block action-from-profile-alone", description: "Cannot trigger arrest/search warrants", enforcement: "DENY" }
    ],
    policyRules: [
      { toolname: "predictive_policing", ruletype: "DENY", description: "Profiling blocker" },
      { toolname: "warrant_generation", ruletype: "DENY", description: "Block action-from-profile-alone" }
    ]
  },
  {
    id: "migration-border",
    annexCategory: 7,
    name: "Migration & Border",
    description: "Migration, asylum and border control management.",
    complianceDeadline: "2026-08-02",
    conformityAssessment: "self",
    riskLevel: "high",
    version: "1.0.0",
    baselineControls: BASELINE_CONTROLS,
    sectorOverrides: [
      { id: "block-autonomous-asylum", name: "Block autonomous asylum decisions", description: "Human required for asylum rejections", enforcement: "DENY" },
      { id: "risk-scores-review", name: "Mandatory review for risk scores", description: "Border risk scoring needs human verification", enforcement: "REQUIRE_APPROVAL" },
      { id: "anti-discrimination-check", name: "Anti-discrimination data check", description: "Monitors input data for protected classes", enforcement: "logging" }
    ],
    policyRules: [
      { toolname: "asylum_decision", ruletype: "REQUIRE_APPROVAL", condition: "decision == 'reject'", description: "Block autonomous asylum rejections" },
      { toolname: "border_risk_score", ruletype: "REQUIRE_APPROVAL", description: "Mandatory review for risk scores" }
    ]
  },
  {
    id: "justice-democracy",
    annexCategory: 8,
    name: "Justice & Democracy",
    description: "Administration of justice and democratic processes.",
    complianceDeadline: "2026-08-02",
    conformityAssessment: "self",
    riskLevel: "high",
    version: "1.0.0",
    baselineControls: BASELINE_CONTROLS,
    sectorOverrides: [
      { id: "non-binding-label", name: "Non-binding label on outputs", description: "All outputs must be labeled 'assisting only'", enforcement: "flag" },
      { id: "sentencing-blocker", name: "Sentencing recommendation blocker", description: "Cannot output jail time recommendations", enforcement: "DENY" },
      { id: "electoral-influence-block", name: "Electoral influence hard-disable", description: "Cannot generate deepfakes for elections", enforcement: "DENY" }
    ],
    policyRules: [
      { toolname: "sentencing_calculator", ruletype: "DENY", description: "Sentencing recommendation blocker" },
      { toolname: "content_generation", ruletype: "DENY", condition: "topic == 'election_campaign'", description: "Electoral influence hard-disable" }
    ]
  },
  {
    id: "banking-finance",
    annexCategory: null,  // DORA compliance (not EU AI Act Annex III)
    name: "Banking & Finance",
    description: "AI systems for credit scoring and evaluation of creditworthiness. DORA-regulated sector (Digital Operational Resilience Act).",
    complianceDeadline: "2026-08-02",
    conformityAssessment: "self",
    riskLevel: "high",
    version: "1.0.0",
    baselineControls: BASELINE_CONTROLS,
    sectorOverrides: [
      { id: "credit-approval-oversight", name: "Credit approval oversight", description: "Human-in-the-loop for lending decisions", enforcement: "REQUIRE_APPROVAL" },
      { id: "financial-data-shield", name: "Financial data shield", description: "Prevents bulk export of portfolio data", enforcement: "DENY" }
    ],
    policyRules: [
      { toolname: "*", ruletype: "REQUIRE_APPROVAL", condition: "(credit.?score|creditworthiness|credit.?rating)", description: "Credit scoring decisions require human oversight" },
      { toolname: "*", ruletype: "REQUIRE_APPROVAL", condition: "(loan.approval|loan.rejection|mortgage.decision)", description: "Lending decisions must have human review" },
      { toolname: "*", ruletype: "REQUIRE_APPROVAL", condition: "(transfer|wire|payment|transaction).*(amount|usd|eur|gbp)", description: "Human approval required for financial transfers" },
      { toolname: "database", ruletype: "DENY", condition: "bulk.*(export|download).*(customer|account|portfolio)", description: "Prevent bulk export of customer financial data" }
    ]
  }
];

export function getSectorTemplate(id: string): SectorTemplate | undefined {
  return SECTOR_TEMPLATES.find(t => t.id === id);
}
