// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { Pool } from 'pg';
import * as dotenv from 'dotenv';
import * as path from 'path';

dotenv.config({ path: path.join(__dirname, '../.env') });

const pool = new Pool({
  connectionString: process.env.DATABASE_URL
});

async function migrate() {
  console.log('🚀 Starting templates v2 migration...');
  const client = await pool.connect();
  try {
    await client.query('BEGIN');

    // 1. Update agent_templates
    console.log('--- Updating agent_templates table');
    await client.query(`
      ALTER TABLE agent_templates 
      ADD COLUMN IF NOT EXISTS version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
      ADD COLUMN IF NOT EXISTS priority_order INT DEFAULT 0;
    `);
    
    // Add unique constraint if not exists
    await client.query(`
      DO $$
      BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'idx_agent_template_version') THEN
          ALTER TABLE agent_templates ADD CONSTRAINT idx_agent_template_version UNIQUE (agent_id, template_id, version);
        END IF;
      END
      $$;
    `);

    // 2. Update template_compliance_status
    console.log('--- Updating template_compliance_status table');
    await client.query(`
      DO $$
      BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'idx_agent_template_control') THEN
          ALTER TABLE template_compliance_status ADD CONSTRAINT idx_agent_template_control UNIQUE (agent_id, template_id, control_id);
        END IF;
      END
      $$;
    `);

    await client.query('COMMIT');
    console.log('✅ Migration complete!');
  } catch (err) {
    await client.query('ROLLBACK');
    console.log('❌ Migration failed:', err);
  } finally {
    client.release();
    await pool.end();
  }
}

migrate();
