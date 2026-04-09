// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { Router, Request, Response } from "express";
import { pool } from "../db";
import { randomUUID } from "crypto";
import { adminAuth, AuthenticatedRequest } from "../auth";
import { logger } from "../logger";
import { resolveTier, TieredRequest } from "../tier-guard";
import { generateCompliancePDF, ComplianceReportData } from "../compliance/pdf-generator";

const router = Router();

// ─── GET /v1/compliance/status ────────────────────────────────────────────────

router.get("/status", adminAuth, async (req: Request, res: Response) => {
    try {
        const authenticatedTenantId = (req as AuthenticatedRequest).tenantId;
        const { tenantId: queryTenantId } = req.query;
        
        // Security: Ensure query tenantId matches authenticated tenantId
        const tenantId = queryTenantId || authenticatedTenantId;
        if (queryTenantId && queryTenantId !== authenticatedTenantId) {
            return res.status(403).json({ error: "Forbidden: Cannot access compliance status of another tenant" });
        }

        if (!tenantId) return res.status(400).json({ error: "Missing tenantId" });

        const [approvalResult, auditResult, denyResult, oldestResult, recentResult] = await Promise.all([
            pool.query("SELECT COUNT(*) FROM policies WHERE ruletype = 'REQUIRE_APPROVAL' AND tenantid = $1", [tenantId]),
            pool.query("SELECT COUNT(*) FROM audit_logs WHERE tenantid = $1", [tenantId]),
            pool.query("SELECT COUNT(*) FROM policies WHERE ruletype = 'DENY' AND tenantid = $1", [tenantId]),
            pool.query("SELECT MIN(timestamp) AS oldest FROM audit_logs WHERE tenantid = $1", [tenantId]),
            pool.query("SELECT COUNT(*) FROM audit_logs WHERE tenantid = $1 AND timestamp >= NOW() - INTERVAL '24 hours'", [tenantId]),
        ]);

        const approvalPolicies = parseInt(approvalResult.rows[0].count, 10);
        const auditCount = parseInt(auditResult.rows[0].count, 10);
        const denyPolicies = parseInt(denyResult.rows[0].count, 10);
        const oldestDate: Date | null = oldestResult.rows[0].oldest;
        const recentCount = parseInt(recentResult.rows[0].count, 10);

        // Record keeping: need (1) logs existing for 30+ days AND (2) recent logs in last 24h (confirming logs still being written)
        let recordStatus: "pass" | "partial" | "fail" = "fail";
        let recordDetail = "No audit logs found";
        if (auditCount > 0 && oldestDate) {
            const daysDiff = Math.floor((Date.now() - oldestDate.getTime()) / 86_400_000);
            const has30DayRetention = daysDiff >= 30;
            const hasRecentLogs = recentCount > 0;
            recordStatus = has30DayRetention && hasRecentLogs ? "pass" : "partial";
            recordDetail = `Logs retained since ${oldestDate.toISOString().split("T")[0]}${!hasRecentLogs ? " (no recent logs in 24h)" : ""}`;
        }

        const checks = {
            humanOversight: {
                status: (approvalPolicies > 0 ? "pass" : "fail") as "pass" | "partial" | "fail",
                detail: approvalPolicies > 0
                    ? `${approvalPolicies} REQUIRE_APPROVAL ${approvalPolicies === 1 ? "policy" : "policies"} active`
                    : "No REQUIRE_APPROVAL policies configured",
            },
            auditLogging: {
                status: (auditCount > 0 ? "pass" : "fail") as "pass" | "partial" | "fail",
                detail: auditCount > 0
                    ? `${auditCount.toLocaleString()} events logged`
                    : "No audit events recorded",
            },
            riskControls: {
                status: (denyPolicies > 0 ? "pass" : "fail") as "pass" | "partial" | "fail",
                detail: denyPolicies > 0
                    ? `${denyPolicies} DENY ${denyPolicies === 1 ? "policy" : "policies"} active`
                    : "No DENY policies configured",
            },
            recordKeeping: {
                status: recordStatus,
                detail: recordDetail,
            },
            dataGovernance: {
                status: (denyPolicies > 0 && approvalPolicies > 0 && auditCount > 0 ? "pass" : (denyPolicies > 0 || approvalPolicies > 0 || auditCount > 0 ? "partial" : "fail")) as "pass" | "partial" | "fail",
                detail: (denyPolicies > 0 && approvalPolicies > 0 && auditCount > 0)
                    ? "Data governance controls enabled: policies + audit logging active"
                    : (denyPolicies > 0 || approvalPolicies > 0 || auditCount > 0)
                    ? `Partial: ${[denyPolicies > 0 ? "access controls" : "", approvalPolicies > 0 ? "approvals" : "", auditCount > 0 ? "logging" : ""].filter(Boolean).join(", ")}`
                    : "No data governance controls configured",
            },
            incidentLogging: {
                status: (denyPolicies > 0 ? "pass" : (auditCount > 0 ? "partial" : "fail")) as "pass" | "partial" | "fail",
                detail: denyPolicies > 0
                    ? `${denyPolicies} DENY ${denyPolicies === 1 ? "policy" : "policies"} configured (incidents detected)`
                    : auditCount > 0
                    ? `Audit logging active (${auditCount.toLocaleString()} events) but no incident policies defined`
                    : "No incident response policies configured",
            },
        };

        const criticalFailed = (["humanOversight", "auditLogging", "riskControls"] as const).some(
            (k) => checks[k].status === "fail"
        );
        const anyNonPass = Object.values(checks).some((c) => c.status !== "pass");

        const overall = criticalFailed
            ? "NOT_CONFIGURED"
            : anyNonPass
            ? "ATTENTION_NEEDED"
            : "COMPLIANT";

        res.json({ overall, checks, lastChecked: new Date().toISOString() });
    } catch (e) {
        logger.error("[Compliance] Status error:", { error: e });
        res.status(500).json({ 
            error: "Internal Server Error", 
            message: e instanceof Error ? e.message : String(e) 
        });
    }
});

// ─── GET /v1/compliance/report ────────────────────────────────────────────────

router.get("/report", adminAuth, resolveTier, async (req: Request, res: Response) => {
    try {
        const authenticatedTenantId = (req as AuthenticatedRequest).tenantId;
        const { agentId, tenantId: queryTenantId } = req.query;
        
        // Security: Ensure query tenantId matches authenticated tenantId
        const tenantId = queryTenantId || authenticatedTenantId;
        if (queryTenantId && queryTenantId !== authenticatedTenantId) {
            return res.status(403).json({ error: "Forbidden: Cannot access compliance report of another tenant" });
        }

        if (!tenantId) return res.status(400).json({ error: "Missing tenantId" });

        const tieredReq = req as TieredRequest;
        const tierLimits = tieredReq.tierLimits!;

        // --- Tier Enforcement: PDF Reports are paid-only ---
        if (!tierLimits.pdfReports) {
            return res.status(403).json({
                error: "PDF compliance reports require a paid plan.",
                detail: "Your Developer tier includes JSON compliance status via /v1/compliance/status. Upgrade to Starter ($49/mo) or higher for regulator-ready PDF evidence reports.",
                upgradeUrl: "https://www.supra-wall.com/pricing",
                code: "TIER_LIMIT_EXCEEDED",
                currentTier: tieredReq.tier,
            });
        }

        const to = req.query.to ? new Date(req.query.to as string) : new Date();
        const from = req.query.from
            ? new Date(req.query.from as string)
            : new Date(Date.now() - 30 * 86_400_000);

        // Fetch audit logs scoped to tenant
        const auditParams: (Date | string)[] = [from, to, tenantId as string];
        let auditSql = "SELECT * FROM audit_logs WHERE timestamp >= $1 AND timestamp <= $2 AND tenantid = $3";
        if (agentId) {
            auditSql += " AND agentid = $4";
            auditParams.push(agentId as string);
        }
        auditSql += " ORDER BY timestamp DESC";

        // Fetch policies scoped to tenant
        const policyParams: string[] = [tenantId as string];
        let policySql = "SELECT * FROM policies WHERE tenantid = $1";
        if (agentId) {
            policySql += " AND agentid = $2";
            policyParams.push(agentId as string);
        }
        policySql += " ORDER BY created_at ASC";

        const [auditResult, policyResult] = await Promise.all([
            pool.query(auditSql, auditParams),
            pool.query(policySql, policyParams),
        ]);

        const logs = auditResult.rows;

        // Calculate real compliance score from template_compliance_status
        let complianceScore = 0;
        try {
            const scoreResult = await pool.query(
                `SELECT COUNT(*) as total, SUM(CASE WHEN status = 'compliant' THEN 1 ELSE 0 END) as compliant FROM template_compliance_status WHERE agent_id = $1`,
                [agentId || tenantId]
            );
            if (scoreResult.rows[0]?.total > 0) {
                const total = parseInt(scoreResult.rows[0].total, 10);
                const compliant = parseInt(scoreResult.rows[0].compliant || 0, 10);
                complianceScore = Math.round((compliant / total) * 100);
            }
        } catch (e) {
            logger.warn("[Compliance] Failed to calculate compliance score:", { error: e });
            complianceScore = 0;
        }

        // Prepare template data
        const reportId = randomUUID().substring(0, 8).toUpperCase();
        const dateStr = new Date().toISOString().split("T")[0];

        const reportData: ComplianceReportData = {
            issueDate: new Date().toLocaleDateString(),
            tenantId: tenantId as string,
            reportId: `SW-COMP-${reportId}`,
            totalEvaluations: logs.length,
            threatsBlocked: logs.filter(l => l.decision === "DENY").length,
            complianceScore,
            signature: "", // Will be generated in pdf-generator
            events: logs.map(l => ({
                timestamp: new Date(l.timestamp).toLocaleString(),
                agentName: l.agentid.substring(0, 8), // Simplify or lookup name if available
                toolName: l.toolname,
                riskScore: l.riskscore || 0,
                decision: l.decision
            }))
        };

        const templateName = req.query.template as string || "eu-ai-act-article-9";

        // Whitelist valid template names to prevent path traversal
        const VALID_TEMPLATES = new Set([
            'eu-ai-act-article-9',
            'sector-hr-employment',
            'sector-healthcare',
            'sector-biometrics',
            'sector-critical-infrastructure',
            'sector-education',
            'sector-law-enforcement',
            'sector-migration-border',
            'sector-justice-democracy'
        ]);

        if (!VALID_TEMPLATES.has(templateName)) {
            return res.status(400).json({ error: "Invalid template name" });
        }

        const pdf = await generateCompliancePDF(templateName, reportData);

        res.setHeader("Content-Type", "application/pdf");
        res.setHeader(
            "Content-Disposition",
            `attachment; filename="suprawall-compliance-${templateName}-${dateStr}.pdf"`
        );
        res.send(pdf);
    } catch (e) {
        logger.error("[Compliance] Report error:", { error: e });
        if (!res.headersSent) {
            res.status(500).json({ error: "Internal Server Error" });
        }
    }
});

export default router;
