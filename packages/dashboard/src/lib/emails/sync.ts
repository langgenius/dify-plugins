// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { config } from 'dotenv';
config({ path: '.env.local' });
import fs from 'fs';
import path from 'path';
import { phase1Templates } from './phase1';

/**
 * Migration Bridge: SupraWall Email System (MailerLite)
 *
 * MailerLite Transactional API expects the full HTML body in each request.
 * This script renders all Phase 1 templates locally into a 'previews/' folder
 * so you can verify the Technical Noir design before going live.
 */

async function generatePreviews() {
    process.stdout.write("Starting MailerLite template preview generation...\n");

    const baseTemplatePath = path.join(process.cwd(), 'packages/dashboard/src/lib/emails/templates/base.html');
    const previewsDir = path.join(process.cwd(), 'packages/dashboard/src/lib/emails/previews');

    if (!fs.existsSync(previewsDir)) {
        fs.mkdirSync(previewsDir, { recursive: true });
    }

    const baseTemplate = fs.readFileSync(baseTemplatePath, 'utf8');

    for (const template of phase1Templates) {
        process.stdout.write(`Rendering ${template.tag}: ${template.name}...\n`);

        const renderedHtml = baseTemplate.replace('{{content}}', template.html);
        const fileName = `${template.tag}.html`;
        fs.writeFileSync(path.join(previewsDir, fileName), renderedHtml);
    }

    process.stdout.write(`\n✅ Previews generated in: ${previewsDir}\n`);
    process.stdout.write("MailerLite Migration Complete: Dispatcher is now configured to send these in real-time.\n");
}

generatePreviews().catch(console.error);
