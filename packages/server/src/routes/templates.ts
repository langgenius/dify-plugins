// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { Router } from "express";
import { gatekeeperAuth } from "../auth";
import { SECTOR_TEMPLATES, getSectorTemplate } from "@suprawall/core";
import { pool } from "../db";

const router = Router();

// GET /api/v1/templates - Returns all 8 templates with metadata
router.get("/", gatekeeperAuth, (req, res) => {
  res.status(200).json({ templates: SECTOR_TEMPLATES });
});

// GET /api/v1/templates/:id - Returns single template detail
router.get("/:id", gatekeeperAuth, (req, res) => {
  const template = getSectorTemplate(req.params.id as string);
  if (!template) {
    return res.status(404).json({ error: "Template not found" });
  }
  res.status(200).json({ template });
});

// GET /api/v1/templates/status - Returns compliance status for all agents in tenant
router.get("/status", gatekeeperAuth, async (req, res) => {
  // @ts-ignore
  const tenantId = req.user?.tenantId;
  if (!tenantId) return res.status(401).json({ error: "Unauthorized" });

  try {
    const status = await pool.query(
      `SELECT 
        a.id as agentId, a.name as agentName,
        t.template_id, t.version,
        cs.control_id, cs.status, cs.last_checked
       FROM agents a
       JOIN agent_templates t ON a.id = t.agent_id
       LEFT JOIN template_compliance_status cs ON a.id = cs.agent_id AND t.template_id = cs.template_id
       WHERE a.tenantid = $1 AND t.is_active = TRUE`,
      [tenantId]
    );

    // Group by agent
    const grouped = status.rows.reduce((acc, row) => {
      if (!acc[row.agentid || row.agentId]) {
        acc[row.agentid || row.agentId] = {
          agentId: row.agentid || row.agentId,
          agentName: row.agentname,
          templates: []
        };
      }
      
      const agent = acc[row.agentid || row.agentId];
      let template = agent.templates.find((t: any) => t.id === row.template_id);
      if (!template) {
        template = { id: row.template_id, version: row.version, controls: [] };
        agent.templates.push(template);
      }
      
      if (row.control_id) {
        template.controls.push({
          id: row.control_id,
          status: row.status,
          lastChecked: row.last_checked
        });
      }
      
      return acc;
    }, {} as any);

    res.status(200).json({ status: Object.values(grouped) });
  } catch (err) {
    console.error("[TemplatesAPI] Failed to fetch tenant status:", err);
    res.status(500).json({ error: "Failed to fetch status" });
  }
});

// GET /api/v1/templates/status/:agentId - Returns compliance status for an agent
router.get("/status/:agentId", gatekeeperAuth, async (req, res) => {
  const { agentId } = req.params;
  try {
    const templates = await pool.query(
      `SELECT t.* FROM agent_templates t WHERE t.agent_id = $1 AND t.is_active = TRUE ORDER BY t.priority_order ASC`,
      [agentId]
    );

    const controls = await pool.query(
      `SELECT * FROM template_compliance_status WHERE agent_id = $1`,
      [agentId]
    );

    res.status(200).json({
      agentId,
      appliedTemplates: templates.rows,
      complianceStatus: controls.rows,
      lastUpdated: new Date().toISOString()
    });
  } catch (err) {
    console.error("[TemplatesAPI] Failed to fetch status:", err);
    res.status(500).json({ error: "Failed to fetch compliance status" });
  }
});

// POST /api/v1/templates/apply - Applies a template to an agent (Standard Snapshot)
router.post("/apply", gatekeeperAuth, async (req, res) => {
  const { agentId, templateId, customOverrides, version = '1.0.0' } = req.body;
  if (!agentId || !templateId) {
    return res.status(400).json({ error: "Missing agentId or templateId" });
  }

  const template = getSectorTemplate(templateId as string);
  if (!template) {
    return res.status(404).json({ error: "Template not found" });
  }

  // @ts-ignore
  const tenantId = req.user?.tenantId;
  if (!tenantId) {
    return res.status(401).json({ error: "Unauthorized: Missing tenant context" });
  }

  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    // 1. Check for existing assignment of THIS version
    const existing = await client.query(
      `SELECT id FROM agent_templates WHERE agent_id = $1 AND template_id = $2 AND version = $3`,
      [agentId, templateId, version]
    );

    if (existing.rowCount && existing.rowCount > 0) {
      await client.query('ROLLBACK');
      return res.status(409).json({ error: "Template version already applied to this agent" });
    }

    // 2. Insert into agent_templates
    await client.query(
      `INSERT INTO agent_templates (agent_id, template_id, version, custom_overrides, applied_by) 
       VALUES ($1, $2, $3, $4, $5)`,
      [agentId, templateId, version, JSON.stringify(customOverrides || {}), tenantId]
    );

    // 3. Insert into template_compliance_status for each control
    const allControls = [
      ...template.baselineControls.map(c => c.id),
      ...template.sectorOverrides.map(c => c.id)
    ];

    for (const controlId of allControls) {
      await client.query(
        `INSERT INTO template_compliance_status (agent_id, template_id, control_id, status)
         VALUES ($1, $2, $3, 'pending')
         ON CONFLICT (agent_id, template_id, control_id) DO NOTHING`,
        [agentId, templateId, controlId]
      );
    }

    // 4. Generate policy rules from template config
    for (const rule of template.policyRules) {
      await client.query(
        `INSERT INTO policies (tenantid, agentid, toolname, ruletype, condition, description)
         VALUES ($1, $2, $3, $4, $5, $6)`,
        [tenantId, agentId, rule.toolname, rule.ruletype, rule.condition || null, `[${template.name} v${version}] ${rule.description}`]
      );
    }

    await client.query('COMMIT');

    res.status(200).json({
      message: "Template applied successfully",
      template: template.name,
      version,
      controlsConfigured: allControls.length,
      policiesCreated: template.policyRules.length
    });
  } catch (err) {
    await client.query('ROLLBACK');
    console.error("[TemplatesAPI] Failed to apply template:", err);
    res.status(500).json({ error: "Failed to apply template" });
  } finally {
    client.release();
  }
});

export default router;
