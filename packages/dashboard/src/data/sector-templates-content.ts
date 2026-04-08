// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

export interface SectorContent {
  id: string;
  name: string;
  annexCategory: number;
  heroTitle: string;
  heroDescription: string;
  whatItCovers: string[];
  whyHighRisk: string;
  keyControls: string[];
  conformityType: string;
  primaryKeyword: string;
}

export const SECTOR_MARKETING_CONTENT: Record<string, SectorContent> = {
  'hr-employment': {
    id: 'hr-employment',
    name: 'HR & Employment',
    annexCategory: 4,
    heroTitle: 'EU AI Act HR Compliance Template for AI Agents',
    heroDescription: 'Automate compliance for AI-driven recruitment, CV screening, and worker management. Pre-configured policies aligned with Annex III Section 4.',
    whatItCovers: [
      'Recruitment and selection (CV screening, candidate ranking)',
      'Promotion and termination decisions',
      'Task allocation and monitoring of worker performance',
      'Access to self-employment opportunities'
    ],
    whyHighRisk: 'AI systems in HR can significantly impact career paths and livelihoods. The EU AI Act classifies these as high-risk to prevent bias and ensure fair treatment for workers and job seekers.',
    keyControls: [
      'Bias audit trail for diversity & inclusion monitoring',
      'Human-in-the-loop requirement for hiring/firing decisions',
      'Mandatory employee notification protocols',
      'GDPR DPIA integration for automated processing'
    ],
    conformityType: 'Self-assessment (Internal Control)',
    primaryKeyword: 'eu ai act hr compliance template'
  },
  'healthcare': {
    id: 'healthcare',
    name: 'Healthcare',
    annexCategory: 5,
    heroTitle: 'Healthcare AI Compliance Template for EU AI Act',
    heroDescription: 'Secure AI medical devices, triage systems, and insurance processing. Built-in PHI governance and Annex III Section 5 alignment.',
    whatItCovers: [
      'Triage and patient prioritization',
      'Medical insurance eligibility and benefits',
      'AI-enhanced medical imaging and diagnostics',
      'Emergency healthcare access management'
    ],
    whyHighRisk: 'Healthcare AI decisions directly affect physical safety and access to essential life-saving services. High-risk classification ensures clinical safety and prevents discriminatory access to care.',
    keyControls: [
      'PHI data governance and logging shredding',
      '72-hour breach notification workflow',
      'CE marking integration for medical devices',
      'Strict explainability for diagnostic support'
    ],
    conformityType: 'Third-party assessment (Notified Body)',
    primaryKeyword: 'eu ai act healthcare compliance'
  },
  'education': {
    id: 'education',
    name: 'Education',
    annexCategory: 3,
    heroTitle: 'Education AI Compliance Template (Annex III)',
    heroDescription: 'Ensure fair admissions, automated grading, and proctoring. Designed for universities and vocational training providers.',
    whatItCovers: [
      'Admission to educational institutions',
      'Automated grading and performance evaluation',
      'AI proctoring and behavioral monitoring during exams',
      'Vocational training access and scoring'
    ],
    whyHighRisk: 'AI in education can determine an individual\'s future education and professional prospects. High-risk status prevents systemic bias in student evaluation and access to learning.',
    keyControls: [
      'Block autonomous admission rejections',
      'Explainability logs for all student scores',
      'Human oversight for exam proctoring flags',
      'Accessibility check for AI teaching tools'
    ],
    conformityType: 'Self-assessment (Internal Control)',
    primaryKeyword: 'eu ai act education ai compliance'
  },
  'critical-infrastructure': {
    id: 'critical-infrastructure',
    name: 'Critical Infrastructure',
    annexCategory: 2,
    heroTitle: 'Critical Infrastructure AI Safety Template',
    heroDescription: 'Manage energy, water, and traffic safety with AI while meeting strict EU AI Act safety standards.',
    whatItCovers: [
      'Management of road, rail, and air traffic',
      'Water supply and distribution management',
      'Energy grid stability and optimization',
      'Digital infrastructure operation'
    ],
    whyHighRisk: 'Failures in these AI systems can lead to massive environmental damage, loss of life, or large-scale disruption of essential public utilities.',
    keyControls: [
      'Hard failsafe API kill switch',
      'Real-time continuous logging (no buffering)',
      'Human confirmation for all physical actions',
      'Disconnection safety mode (fails safe)'
    ],
    conformityType: 'Self-assessment (Internal Control)',
    primaryKeyword: 'eu ai act critical infrastructure ai'
  },
  'biometrics': {
    id: 'biometrics',
    name: 'Biometrics',
    annexCategory: 1,
    heroTitle: 'Biometric AI Identification Compliance Template',
    heroDescription: 'Regulate facial recognition, emotion detection, and biometric categorization with ultra-strict AI Act controls.',
    whatItCovers: [
      'Remote biometric identification systems',
      'Biometric categorization based on sensitive traits',
      'Emotion recognition in work or school settings',
      'Liveness detection and spoofing prevention'
    ],
    whyHighRisk: 'Biometric systems represent the highest risk to privacy and fundamental rights, especially when used for surveillance or categorization in public spaces.',
    keyControls: [
      'Block real-time public ID (Hard Toggle)',
      'Emotion-recognition scope limiters',
      'Third-party auditor lock requirement',
      'Per-event forensic logging'
    ],
    conformityType: 'Third-party assessment (Notified Body)',
    primaryKeyword: 'eu ai act biometrics compliance'
  },
  'law-enforcement': {
    id: 'law-enforcement',
    name: 'Law Enforcement',
    annexCategory: 6,
    heroTitle: 'Law Enforcement AI Governance Template',
    heroDescription: 'Deploy AI for predictive policing, evidence analysis, and risk assessment while maintaining citizens\' rights.',
    whatItCovers: [
      'Individual risk assessments for recidivism',
      'Deepfake detection in forensic evidence',
      'Polygraphs and similar emotional analysis tools',
      'Predictive policing for crime hotspots'
    ],
    whyHighRisk: 'The use of AI by law enforcement has direct impacts on freedom and the right to a fair trial. The AI Act imposes strict transparency to prevent profiling and abuse.',
    keyControls: [
      'Profiling blocker (anti-discrimination)',
      'Mandatory probabilistic labeling for outputs',
      'Block autonomous warrant generation',
      'Chain-of-custody logging for AI outputs'
    ],
    conformityType: 'Third-party assessment (Notified Body)',
    primaryKeyword: 'eu ai act law enforcement ai'
  },
  'migration-border': {
    id: 'migration-border',
    name: 'Migration & Border',
    annexCategory: 7,
    heroTitle: 'Migration & Border Control AI Compliance',
    heroDescription: 'Secure AI for asylum applications, visa processing, and border security management.',
    whatItCovers: [
      'Polygraphs for immigration processing',
      'Asylum application risk assessment',
      'Visa applicant screening and categorization',
      'Border surveillance and security monitoring'
    ],
    whyHighRisk: 'Vulnerable individuals in migration contexts require high levels of protection. The AI Act ensures that AI does not lead to illegal refoulement or discrimination.',
    keyControls: [
      'Block autonomous asylum rejections',
      'Human review for all border risk scores',
      'Anti-discrimination input monitoring',
      'Multilingual transparency requirements'
    ],
    conformityType: 'Self-assessment (Internal Control)',
    primaryKeyword: 'eu ai act migration ai compliance'
  },
  'justice-democracy': {
    id: 'justice-democracy',
    name: 'Justice & Democracy',
    annexCategory: 8,
    heroTitle: 'Justice & Democracy AI Safety Template',
    heroDescription: 'Govern AI used in courtrooms, legal research, and democratic processes (elections).',
    whatItCovers: [
      'AI assisting judicial authorities in research',
      'AI influencing democratic processes (voter behavior)',
      'Electoral campaign management tools',
      'Online platform moderation for elections'
    ],
    whyHighRisk: 'AI influence in the justice system or democratic elections can undermine the rule of law and the democratic foundation of society.',
    keyControls: [
      'Non-binding labels on judicial outputs',
      'Sentencing recommendation blocker',
      'Electoral influence deepfake filter',
      'Full explainability for judicial research'
    ],
    conformityType: 'Self-assessment (Internal Control)',
    primaryKeyword: 'eu ai act justice ai compliance'
  }
};
