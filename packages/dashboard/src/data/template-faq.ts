// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

export interface FAQItem {
  question: string;
  answer: string;
}

export const TEMPLATE_CLUSTER_FAQ: Record<string, FAQItem[]> = {
  'hub': [
    {
      question: "What are EU AI Act Compliance Templates?",
      answer: "Templates are pre-configured security and governance policies that map your AI agent actions to the specific requirements of the EU AI Act's High-Risk categories (Annex III). They automate the setup of human oversight, logging, and risk management."
    },
    {
      question: "Which Annex III sector does my agent fall into?",
      answer: "It depends on the purpose of your agent and its data. Our compliance quiz helps you identify if your use case falls under HR, Healthcare, Education, or any of the 8 Annex III sectors."
    },
    {
      question: "What happens if I apply multiple templates?",
      answer: "SupraWall allows you to stack templates. If an agent operates in both HR and Education, the system will apply the strictest common denominator of controls and combine the sector-specific logging requirements."
    },
    {
      question: "Do these templates ensure 100% legal compliance?",
      answer: "Templates automate the technical enforcement (Article 9, 12, 14, etc.), which is the most difficult part of compliance. However, you still need to complete your Quality Management System (Article 17) and legal documentation."
    },
    {
      question: "What is the deadline for Annex III compliance?",
      answer: "High-risk AI systems already on the market or being placed on the market must be compliant by August 2, 2026."
    }
  ],
  'hr-employment': [
    {
      question: "Is CV screening high-risk under the EU AI Act?",
      answer: "Yes, systems used for recruitment, including for advertising vacancies and screening or filtering applications, are classified as high-risk under Annex III, Section 4."
    },
    {
      question: "Can I still use AI for performance monitoring?",
      answer: "Yes, but you must implement human oversight, transparency, and data governance controls. Our HR template enforces these automatically."
    }
  ],
  'healthcare': [
    {
      question: "When does a healthcare agent require a Notified Body?",
      answer: "If your AI system is considered an AI medical device or falls under specific health insurance categorization, a third-party conformity assessment (Notified Body) is typically required."
    }
  ]
};
