// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

export interface EmailTemplateSpec {
  id: string;
  name: string;
  subject: string;
  category: string;
  type: 'automation' | 'transactional' | 'marketing';
  sender: 'security' | 'team';
  description: string;
  content: string;
}

export const phase1Templates: EmailTemplateSpec[] = [
  {
    id: "SW-T-001",
    name: "Welcome & First Steps",
    category: "Onboarding Sequence",
    type: "automation",
    sender: "team",
    subject: "Your AI agents now have a security layer — here's how to activate it",
    description: "Drive first integration within 24h.",
    content: `
      <h1>Welcome to the shield.</h1>
      <p>SupraWall is now ready to protect your AI agents. You're one step away from runtime security, budget circuit-breakers, and automated compliance.</p>
      
      <h3>3-Step Quickstart</h3>
      <ol>
        <li><strong>Install the SDK:</strong> <br><code>npm install @suprawall/sdk</code></li>
        <li><strong>Wrap your Agent:</strong> Use our <code>secureAgent</code> wrapper on your LangChain, CrewAI, or AutoGen agent.</li>
        <li><strong>See Interception:</strong> Run your agent and watch the dashboard light up.</li>
      </ol>

      <a href="https://app.supra-wall.com/dashboard?setup=true" class="btn">Run your first interception</a>
      
      <p style="font-size: 14px; color: #666666;">Need help? Check our docs for <a href="#" style="color: #B8FF00;">LangChain</a>, <a href="#" style="color: #B8FF00;">CrewAI</a>, or <a href="#" style="color: #B8FF00;">AutoGen</a>.</p>
    `
  },
  {
    id: "SW-T-002",
    name: "First Interception Detected",
    category: "Onboarding Sequence",
    type: "automation",
    sender: "team",
    subject: "Your first interception is live — here's what just happened",
    description: "Create the aha moment with dynamic data.",
    content: `
      <h1>System active.</h1>
      <p>Your agent just made its first protected call. SupraWall intercepted the request, performed semantic analysis, and applied your security policies in real-time.</p>
      
      <div class="code-block">
        <strong>INTERCEPTION EVENT LOG</strong><br>
        Framework: {{framework}}<br>
        Tool: {{tool_name}}<br>
        Decision: <span style="color: {{decision_color}}">{{decision}}</span><br>
        Timestamp: {{timestamp}}
      </div>

      <p>This is just the beginning. You can now set granular rules to block database deletions, require human approval for payments, or scrub PII automatically.</p>

      <a href="https://app.supra-wall.com/dashboard/intercepts" class="btn">See all intercepted calls</a>
    `
  },
  {
    id: "SW-HITL-001",
    name: "HITL Approval Request",
    category: "HITL Workflow",
    type: "transactional",
    sender: "security",
    subject: "Action awaiting your approval — {{agent_name}} wants to {{action_summary}}",
    description: "Mobile-friendly approval decisions.",
    content: `
      <div class="badge badge-warn">APPROVAL REQUIRED</div>
      <h1>Action Pending.</h1>
      <p>An autonomous agent is requesting permission to execute a high-risk operation.</p>
      
      <div style="background-color: #1A1A1A; padding: 20px; border-radius: 6px; margin: 20px 0;">
        <p style="margin: 0; font-size: 14px; color: #888888;">AGENT</p>
        <p style="margin: 5px 0 15px 0; font-weight: 700;">{{agent_name}}</p>
        
        <p style="margin: 0; font-size: 14px; color: #888888;">REQUESTED ACTION</p>
        <p style="margin: 5px 0 15px 0; font-family: monospace; color: #B8FF00;">{{tool_name}}({{params}})</p>
        
        <p style="margin: 0; font-size: 14px; color: #888888;">RISK LEVEL</p>
        <p style="margin: 5px 0 0 0; color: #FFAB00;">{{risk_level}}</p>
      </div>

      <div style="text-align: center;">
        <a href="{{approve_url}}" class="btn" style="margin-right: 10px; width: 40%;">✅ APPROVE</a>
        <a href="{{deny_url}}" class="btn btn-danger" style="width: 40%;">❌ DENY</a>
      </div>

      <p style="text-align: center; font-size: 12px; color: #666666; margin-top: 20px;">
        Decision window expires in {{expiry_time}}. Review full context in the <a href="{{dashboard_url}}" style="color: #B8FF00;">SupraWall Dashboard</a>.
      </p>
    `
  },
  {
    id: "SW-A-001",
    name: "Budget Alert 80%",
    category: "Security & Runtime Alerts",
    type: "transactional",
    sender: "security",
    subject: "⚠️ Budget alert: Agent '{{agent_name}}' is at 80% of its \${{limit}} cap",
    description: "Prevent runaway costs.",
    content: `
      <div class="badge badge-warn">BUDGET WARNING</div>
      <h1>Limit approaching.</h1>
      <p>Agent '<strong>{{agent_name}}</strong>' has consumed 80% of its allocated budget for the current period.</p>
      
      <div style="margin: 30px 0;">
        <div style="height: 12px; background-color: #222222; border-radius: 6px; overflow: hidden;">
          <div style="width: 80%; height: 100%; background-color: #FFAB00;"></div>
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 10px; font-size: 14px;">
          <span>\${{current_spend}} spent</span>
          <span>\${{limit}} limit</span>
        </div>
      </div>

      <div class="code-block" style="color: #E0E0E0;">
        <strong>FORECAST</strong><br>
        Current rate: \${{burn_rate}}/hr<br>
        Time to cap: {{time_to_cap}}<br>
        Projected hit: {{hit_timestamp}}
      </div>

      <a href="https://app.supra-wall.com/dashboard/budgets" class="btn">Adjust Budget Cap</a>
      <a href="#" class="btn btn-secondary">Add Approval Rule</a>
    `
  },
  {
    id: "SW-A-003",
    name: "Prompt Injection Detected",
    category: "Security & Runtime Alerts",
    type: "transactional",
    sender: "security",
    subject: "🚨 Prompt injection attempt blocked — agent '{{agent_name}}'",
    description: "Notify security contacts of attacks.",
    content: `
      <div class="badge badge-deny">SECURITY ALERT</div>
      <h1>Attack mitigated.</h1>
      <p>Our Layer 2 semantic firewall just blocked a prompt injection attempt targeting <strong>{{agent_name}}</strong>.</p>
      
      <div class="code-block">
        <strong>THREAT DETAILS</strong><br>
        Pattern: {{threat_type}}<br>
        Decision: DENY (Hard Stop)<br>
        Risk Level: CRITICAL<br>
        Target: {{tool_target}}
      </div>

      <p>The malicious input was scrubbed and the agent execution was halted before any damage could occur.</p>

      <a href="{{incident_log_url}}" class="btn">Review Incident Log</a>
    `
  },
  {
    id: "SW-T-003",
    name: "48h Nudge (No Integration)",
    category: "Onboarding Sequence",
    type: "automation",
    sender: "team",
    subject: "Stuck? Here's a 90-second setup for your AI agent",
    description: "Recover churning users before they disappear.",
    content: `
      <h1>Need a hand?</h1>
      <p>We noticed you haven't integrated SupraWall yet. Most developers get their first agent protected in under 2 minutes.</p>
      
      <h3>Select your framework</h3>
      <div style="margin: 20px 0;">
        <a href="#" class="btn btn-secondary" style="margin-right: 10px;">LangChain</a>
        <a href="#" class="btn btn-secondary" style="margin-right: 10px;">CrewAI</a>
        <a href="#" class="btn btn-secondary">AutoGen</a>
      </div>

      <div class="code-block">
        // CrewAI example<br>
        from suprawall import secure_agent<br>
        <br>
        agent = Agent(role="Researcher", ...)<br>
        agent = secure_agent(agent, policy_id="default")
      </div>

      <p>Reply to this email if you're stuck, or book a 15-min quickstart call with the team.</p>

      <a href="https://calendly.com/suprawall/quickstart" class="btn">Book Onboarding Call</a>
    `
  },
  {
    id: "SW-A-002",
    name: "Budget Cap Hit (Hard Block)",
    category: "Security & Runtime Alerts",
    type: "transactional",
    sender: "security",
    subject: "🛑 Agent '{{agent_name}}' has been stopped — budget cap reached",
    description: "Immediate critical alert. User must take action.",
    content: `
      <div class="badge badge-deny">SYSTEM HALTED</div>
      <h1>Budget Cap Reached.</h1>
      <p>Agent '<strong>{{agent_name}}</strong>' has hit its maximum spending limit of \${{limit}}.</p>
      
      <p>To prevent runaway costs, SupraWall has suspended all tool calls for this agent. Execution will resume once the budget is increased or the period resets.</p>

      <div style="background-color: #1A1A1A; padding: 20px; border-radius: 6px; margin: 20px 0;">
        <p style="margin: 0; font-size: 14px; color: #888888;">TOTAL SPENT</p>
        <p style="margin: 5px 0 15px 0; font-weight: 700; color: #FF4B4B;">\${{spend}}</p>
        
        <p style="margin: 0; font-size: 14px; color: #888888;">STOPPED AT</p>
        <p style="margin: 5px 0 0 0;">{{timestamp}}</p>
      </div>

      <a href="https://app.supra-wall.com/dashboard/budgets?agent={{agent_id}}" class="btn">Increase Budget Cap</a>
      <a href="#" class="btn btn-secondary">Whitelist Emergency Calls</a>
    `
  },
  {
    id: "SW-HITL-002",
    name: "Approval Request Approved",
    category: "HITL Workflow",
    type: "transactional",
    sender: "security",
    subject: "✅ Approved — '{{action}}' will now execute",
    description: "Close the loop for the requester.",
    content: `
      <div class="badge badge-allow">ACTION APPROVED</div>
      <h1>Execution Resumed.</h1>
      <p>The pending action for <strong>{{agent_name}}</strong> was approved by <strong>{{reviewer_name}}</strong>.</p>
      
      <div class="code-block">
        <strong>AUDIT TRAIL</strong><br>
        Action: {{action}}<br>
        Approved By: {{reviewer_name}}<br>
        Timestamp: {{timestamp}}<br>
        Reference ID: {{ref_id}}
      </div>

      <a href="{{log_url}}" class="btn">View Execution Log</a>
    `
  },
  {
    id: "SW-HITL-003",
    name: "Approval Request Denied",
    category: "HITL Workflow",
    type: "transactional",
    sender: "security",
    subject: "❌ Denied — '{{action}}' was blocked by {{reviewer_name}}",
    description: "Notify and enable course-correction.",
    content: `
      <div class="badge badge-deny">ACTION BLOCKED</div>
      <h1>Action Denied.</h1>
      <p>The pending action for <strong>{{agent_name}}</strong> was denied by <strong>{{reviewer_name}}</strong>.</p>
      
      <div style="background-color: #1A1A1A; padding: 20px; border-radius: 6px; margin: 20px 0;">
        <p style="margin: 0; font-size: 14px; color: #888888;">DENIAL REASON</p>
        <p style="margin: 5px 0 0 0; color: #FFFFFF; font-style: italic;">"{{reason}}"</p>
      </div>

      <p>The agent state has been updated, and the operation was skipped to maintain security posture.</p>

      <a href="{{policy_url}}" class="btn">Update Agent Policy</a>
    `
  },
  {
    id: "SW-B-002",
    name: "Free Tier Limit Warning",
    category: "Billing & Plan Management",
    type: "transactional",
    sender: "team",
    subject: "You're at 80% of your free plan — agents protected: {{n}}",
    description: "Convert free users before they hit the wall.",
    content: `
      <div class="badge badge-warn">PLAN QUOTA ALERT</div>
      <h1>Quota approaching.</h1>
      <p>You have reached 80% of the interception limit for the <strong>Free Tier</strong>.</p>
      
      <p>Once you hit 100%, protection will be rate-limited, and some alerts may be delayed. Upgrade now to ensure zero downtime for your runtime guardrails.</p>

      <div style="margin: 30px 0;">
        <div style="height: 12px; background-color: #222222; border-radius: 6px; overflow: hidden;">
          <div style="width: 80%; height: 100%; background-color: #B8FF00;"></div>
        </div>
        <p style="text-align: right; font-size: 14px; margin-top: 5px;">{{usage}}/5,000 interceptions</p>
      </div>

      <a href="https://app.supra-wall.com/dashboard/billing" class="btn">Upgrade to Builder Plan</a>
      
      <div class="divider"></div>
      <p style="font-size: 14px; color: #888888;">The Builder Plan unlocks custom budget circuit-breakers, 50k interceptions, and priority HITL routing.</p>
    `
  },
  {
    id: "SW-B-003",
    name: "Free Tier Limit Reached",
    category: "Billing & Plan Management",
    type: "transactional",
    sender: "team",
    subject: "Your free plan limit is reached — your agents need attention",
    description: "Convert to paid with high urgency.",
    content: `
      <div class="badge badge-deny">QUOTA EXCEEDED</div>
      <h1>Protection Paused.</h1>
      <p>Your account has exceeded the free monthly limit of 5,000 interceptions.</p>
      
      <p style="color: #FF4B4B;">Runtime guardrails are now running in bypass mode. Agents are currently unprotected.</p>

      <div style="background-color: #1A1A1A; padding: 20px; border-radius: 6px; margin: 20px 0; border: 1px solid #FF4B4B;">
        <p style="margin: 0; font-weight: 700;">UPGRADE REQUIRED</p>
        <p style="margin: 10px 0 0 0; font-size: 14px;">Resume security instantly by upgrading to the Builder or Scale plan.</p>
      </div>

      <a href="https://app.supra-wall.com/dashboard/billing" class="btn">Upgrade Now — Resume Protection</a>
    `
  },
  {
    id: "SW-B-004",
    name: "Payment Failed",
    category: "Billing & Plan Management",
    type: "transactional",
    sender: "team",
    subject: "Payment issue — your Suprawall protection needs attention",
    description: "Recover revenue with helpful tone.",
    content: `
      <div class="badge badge-warn">BILLING ISSUE</div>
      <h1>Action needed: Payment failed.</h1>
      <p>We were unable to process the payment for your current billing cycle. To keep your agents protected without interruption, please update your payment method.</p>
      
      <div style="background-color: #1A1A1A; padding: 20px; border-radius: 6px; margin: 20px 0;">
        <p style="margin: 0; font-size: 14px; color: #888888;">PLAN</p>
        <p style="margin: 5px 0 15px 0;">{{plan_name}}</p>
        
        <p style="margin: 0; font-size: 14px; color: #888888;">AMOUNT DUE</p>
        <p style="margin: 5px 0 0 0;">\${{amount}}</p>
      </div>

      <a href="https://app.supra-wall.com/dashboard/billing/payment-methods" class="btn">Update Payment Method</a>
      <p style="font-size: 12px; color: #666666;">We will attempt to re-process the payment in 48 hours. If unsuccessful, your account will be downgraded to the free tier.</p>
    `
  },
  {
    id: "SW-M-001",
    name: "Waitlist Welcome",
    category: "Sales & Enterprise Outreach",
    type: "automation",
    sender: "team",
    subject: "You're on the Suprawall waitlist — what to expect",
    description: "Keep waitlist warm.",
    content: `
      <h1>You're on the list.</h1>
      <p>Thanks for your interest in Suprawall. We're currently rolling out early access to enterprise teams and select open-source contributors.</p>
      
      <div style="background-color: #0A0A0A; border: 1px dashed #B8FF00; padding: 30px; text-align: center; border-radius: 8px; margin: 30px 0;">
        <p style="margin: 0; color: #B8FF00; font-size: 18px; font-weight: 700;">Waitlist Position: #{{position}}</p>
      </div>

      <h3>Want to move up?</h3>
      <p>Share your unique referral link with other AI founders or engineers. For every person who joins, you move up 50 spots.</p>

      <a href="{{referral_link}}" class="btn">Move Up the Waitlist — Share Link</a>
      
      <p style="font-size: 14px; color: #888888; margin-top: 30px;">Follow us on <a href="https://x.com/suprawall" style="color: #B8FF00;">X (@suprawall)</a> for real-time threat intelligence updates.</p>
    `
  },
  {
    id: "SW-M-002",
    name: "Waitlist Access Granted",
    category: "Sales & Enterprise Outreach",
    type: "automation",
    sender: "team",
    subject: "You're in — your Suprawall access is live",
    description: "Convert waitlist to active user.",
    content: `
      <h1>Access Granted.</h1>
      <p>Welcome to the future of AI runtime security. Your SupraWall account is now active and ready for deployment.</p>
      
      <h3>What's included in your Early Access:</h3>
      <ul>
        <li>Full Semantic Firewall (Layer 2)</li>
        <li>PII Scrubbing & Secret Vault</li>
        <li>One-click HITL Approval Workflows</li>
        <li>EU AI Act Baseline Reporting</li>
      </ul>

      <a href="https://app.supra-wall.com/signup/complete?token={{invite_token}}" class="btn">Deploy Your First Protected Agent</a>
      
      <p style="font-size: 14px; color: #888888;">Need a custom demo for your enterprise team? <a href="mailto:team@supra-wall.com" style="color: #B8FF00;">Reply to this email</a>.</p>
    `
  },
  {
    id: "SW-SYS-001",
    name: "Credential Change Notification",
    category: "System & Security Notifications",
    type: "transactional",
    sender: "security",
    subject: "Security notice — your Suprawall credentials were updated",
    description: "Security trust signal. GDPR / SOC2 required.",
    content: `
      <div class="badge badge-warn">SECURITY NOTICE</div>
      <h1>Credentials Updated.</h1>
      <p>This is a formal notification that credentials for your SupraWall account were recently changed.</p>
      
      <div style="background-color: #1A1A1A; padding: 20px; border-radius: 6px; margin: 20px 0;">
        <p style="margin: 0; font-size: 14px; color: #888888;">CHANGE TYPE</p>
        <p style="margin: 5px 0 15px 0;">{{change_type}}</p>
        
        <p style="margin: 0; font-size: 14px; color: #888888;">TIMESTAMP</p>
        <p style="margin: 5px 0 15px 0;">{{timestamp}}</p>
        
        <p style="margin: 0; font-size: 14px; color: #888888;">IP ADDRESS</p>
        <p style="margin: 5px 0 0 0;">{{ip_address}} ({{location}})</p>
      </div>

      <div style="border-left: 4px solid #FF4B4B; padding-left: 20px; margin: 30px 0;">
        <p style="font-weight: 700; color: #FFFFFF; margin-bottom: 5px;">Wasn't you?</p>
        <p style="margin-top: 0; font-size: 14px; color: #888888;">If you did not authorize this change, please contact our security response team immediately.</p>
        <a href="https://app.supra-wall.com/security/emergency" style="color: #FF4B4B; font-weight: 700; text-decoration: none;">LOCK ACCOUNT NOW &rarr;</a>
      </div>
    `
  }
];
