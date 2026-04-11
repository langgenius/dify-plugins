// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import * as core from '@actions/core';
import * as github from '@actions/github';
import axios from 'axios';
import fs from 'fs';
import path from 'path';

async function run() {
  try {
    const apiKey = core.getInput('api-key', { required: false });
    const policyFile = core.getInput('policy-file');
    const failOn = core.getInput('fail-on');
    const agentPath = core.getInput('agent-path');

    core.info('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    core.info('🛡️  SupraWall Security Scan');
    core.info('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

    if (!apiKey) {
        core.setFailed('❌ SupraWall API key not found. Get your free key at https://supra-wall.com/signup');
        return;
    }

    core.info(`🚀 Starting scan in: ${agentPath}`);

    // 1. Detect and Collect Files
    const filesToScan: { path: string; content: string }[] = [];
    const absoluteAgentPath = path.resolve(process.cwd(), agentPath);

    function walk(dir: string) {
      const entries = fs.readdirSync(dir, { withFileTypes: true });
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        const relPath = path.relative(process.cwd(), fullPath);

        if (entry.isDirectory()) {
          if (['node_modules', '.git', 'dist', 'build', 'venv', '__pycache__', '.circleci', '.github'].includes(entry.name)) continue;
          walk(fullPath);
        } else if (entry.isFile()) {
            const ext = path.extname(entry.name).toLowerCase();
            if (['.ts', '.js', '.py', '.tsx', '.jsx'].includes(ext)) {
                const content = fs.readFileSync(fullPath, 'utf8');
                filesToScan.push({ path: relPath, content });
            }
        }
      }
    }

    if (fs.existsSync(absoluteAgentPath)) {
        walk(absoluteAgentPath);
    } else {
        core.setFailed(`Agent path ${agentPath} does not exist.`);
        return;
    }

    core.info(`🔍 Analyzed ${filesToScan.length} files for potential vulnerabilities.`);

    // 2. Load Policy if exists
    let policyContent = null;
    const absolutePolicyPath = path.resolve(process.cwd(), policyFile);
    if (fs.existsSync(absolutePolicyPath)) {
        try {
            policyContent = JSON.parse(fs.readFileSync(absolutePolicyPath, 'utf8'));
            core.info(`📝 Using custom policy from: ${policyFile}`);
        } catch (e) {
            core.warning(`⚠️ Could not parse policy file ${policyFile}. Using default policies.`);
        }
    }

    // 3. POST to SupraWall API
    core.info('📡 Validating agent security with SupraWall AI...');
    
    try {
        const response = await axios.post('https://api.supra-wall.com/v1/scan', {
            files: filesToScan,
            policy: policyContent,
            metadata: {
                repo: `${github.context.repo.owner}/${github.context.repo.repo}`,
                sha: github.context.sha,
                workflow: github.context.workflow
            }
        }, {
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json'
            },
            timeout: 30000 // 30s timeout
        });

        const { status, violations, reportUrl } = response.data;

        // 4. Handle Violations
        if (violations && violations.length > 0) {
            core.warning(`⚠️ Found ${violations.length} security violation(s).`);
            
            for (const v of violations) {
                const annotation = {
                    title: `SupraWall [${v.severity.toUpperCase()}]: ${v.message}`,
                    file: v.file,
                    startLine: v.line || 1
                };

                const msg = `[${v.severity.toUpperCase()}] ${v.message}\nFile: ${v.file}:${v.line || 1}`;
                
                if (v.severity === 'critical' || v.severity === 'high') {
                    core.error(msg, annotation);
                } else {
                    core.warning(msg, annotation);
                }
            }

            core.setOutput('violations', violations.length);
            core.setOutput('report-url', reportUrl);

            // 5. Enforce fail-on
            const severityScale = { 'low': 0, 'medium': 1, 'high': 2, 'critical': 3 };
            const threshold = severityScale[failOn as keyof typeof severityScale] ?? 2; // Default to 'high'

            const highSeverityViolations = violations.filter((v: any) => {
                const sev = severityScale[v.severity as keyof typeof severityScale] ?? 0;
                return sev >= threshold;
            });

            if (highSeverityViolations.length > 0) {
                core.setFailed(`❌ Scan failed with ${highSeverityViolations.length} high-severity violations. Review them at: ${reportUrl}`);
            } else {
                core.info('✅ Scan passed (minor violations found but within threshold).');
            }
        } else {
            core.info('✅ No security violations found. Your agents are secure!');
            core.setOutput('violations', 0);
            core.setOutput('report-url', reportUrl);
        }

        core.info('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        core.info(`📊 View full report: ${reportUrl}`);
        core.info('💡 Get more at: https://www.supra-wall.com/dashboard');
        core.info('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

    } catch (apiErr: any) {
        if (apiErr.response) {
            if (apiErr.response.status === 401) {
                core.setFailed('❌ Unauthorized: Invalid SupraWall API Key. Get a new one or sign up at https://supra-wall.com/signup');
            } else {
                core.setFailed(`❌ SupraWall API rejected the scan request (${apiErr.response.status}). Support: https://discord.gg/suprawall`);
            }
        } else if (apiErr.code === 'ECONNABORTED') {
            core.error('❌ Request timed out. Your project might be too large for a single scan.');
            core.setFailed('Scan timeout.');
        } else {
            core.error(`❌ Network Error: ${apiErr.message}`);
            core.setFailed(`Could not connect to SupraWall API.`);
        }
        
        core.info('💡 Support: https://discord.gg/suprawall');
    }

  } catch (error: any) {
    core.setFailed(error.message);
  }
}

run();
