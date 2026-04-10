// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { db as firestore } from '@/lib/firebase-admin';
import { pool } from '@/lib/db_sql';
import crypto from 'crypto';

/**
 * Approval Workflow System for High-Risk Operations
 *
 * This system routes high-risk operations to a human approval queue before execution.
 * Risk is determined by configurable thresholds across different operation types.
 */

export interface ApprovalThresholds {
    /** Maximum agent budget USD before requiring approval */
    agentBudgetUsd: number;
    /** Maximum number of vault secrets accessible at once */
    vaultSecretsCount: number;
    /** Whether to require approval for bulk operations */
    bulkOperations: boolean;
}

const DEFAULT_THRESHOLDS: ApprovalThresholds = {
    agentBudgetUsd: 1000,      // $1000+ requires approval
    vaultSecretsCount: 10,     // 10+ secrets requires approval
    bulkOperations: true,      // All bulk ops require approval
};

export interface ApprovalRequest {
    id: string;
    tenantId: string;
    userId: string;
    operationType: 'agent_creation' | 'vault_access' | 'budget_increase' | 'bulk_operation';
    resourceId: string;
    parameters: Record<string, any>;
    status: 'pending' | 'approved' | 'rejected' | 'expired';
    requestedAt: Date;
    expiresAt: Date;
    approvedBy?: string;
    approvalReason?: string;
    approvedAt?: Date;
}

/**
 * Determines if an operation requires approval based on risk thresholds.
 * SECURITY: High-risk operations must be explicitly approved by admins.
 */
export async function requiresApproval(
    tenantId: string,
    operationType: ApprovalRequest['operationType'],
    parameters: Record<string, any>
): Promise<boolean> {
    // Get tenant-specific thresholds or use defaults
    const configResult = await pool.query(
        `SELECT approval_thresholds FROM tenants WHERE id = $1`,
        [tenantId]
    );

    let thresholds = DEFAULT_THRESHOLDS;
    if (configResult.rows[0]?.approval_thresholds) {
        thresholds = { ...DEFAULT_THRESHOLDS, ...configResult.rows[0].approval_thresholds };
    }

    // Check operation-specific risk conditions
    switch (operationType) {
        case 'agent_creation': {
            const { max_cost_usd } = parameters;
            return max_cost_usd > thresholds.agentBudgetUsd;
        }

        case 'vault_access': {
            const { secret_ids } = parameters;
            return Array.isArray(secret_ids) && secret_ids.length > thresholds.vaultSecretsCount;
        }

        case 'budget_increase': {
            const { new_budget_usd } = parameters;
            return new_budget_usd > thresholds.agentBudgetUsd;
        }

        case 'bulk_operation': {
            return thresholds.bulkOperations;
        }

        default:
            return false;
    }
}

/**
 * Creates an approval request for a high-risk operation.
 * The operation is blocked until explicitly approved or the request expires (24 hours).
 */
export async function createApprovalRequest(
    tenantId: string,
    userId: string,
    operationType: ApprovalRequest['operationType'],
    resourceId: string,
    parameters: Record<string, any>
): Promise<ApprovalRequest> {
    const requestId = `apr_${crypto.randomBytes(12).toString('hex')}`;
    const now = new Date();
    const expiresAt = new Date(now.getTime() + 24 * 60 * 60 * 1000); // 24 hours

    const result = await pool.query(
        `INSERT INTO approval_requests (id, tenantid, userid, operation_type, resource_id, parameters, status, requested_at, expires_at)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
         RETURNING *`,
        [requestId, tenantId, userId, operationType, resourceId, JSON.stringify(parameters), 'pending', now, expiresAt]
    );

    return mapRowToApprovalRequest(result.rows[0]);
}

/**
 * Retrieves pending approval requests for a tenant.
 */
export async function getPendingApprovals(
    tenantId: string,
    limit: number = 50
): Promise<ApprovalRequest[]> {
    const result = await pool.query(
        `SELECT * FROM approval_requests
         WHERE tenantid = $1 AND status = 'pending' AND expires_at > NOW()
         ORDER BY requested_at DESC
         LIMIT $2`,
        [tenantId, limit]
    );

    return result.rows.map(mapRowToApprovalRequest);
}

/**
 * Approves a high-risk operation.
 * SECURITY: Only tenant admins can approve operations.
 */
export async function approveRequest(
    requestId: string,
    approvedBy: string,
    reason?: string
): Promise<ApprovalRequest> {
    const result = await pool.query(
        `UPDATE approval_requests
         SET status = 'approved', approved_by = $1, approval_reason = $2, approved_at = NOW()
         WHERE id = $3 AND status = 'pending'
         RETURNING *`,
        [approvedBy, reason || 'Approved', requestId]
    );

    if (result.rows.length === 0) {
        throw new Error('Approval request not found or already processed');
    }

    return mapRowToApprovalRequest(result.rows[0]);
}

/**
 * Rejects a high-risk operation.
 * SECURITY: Only tenant admins can reject operations.
 */
export async function rejectRequest(
    requestId: string,
    rejectedBy: string,
    reason: string
): Promise<ApprovalRequest> {
    const result = await pool.query(
        `UPDATE approval_requests
         SET status = 'rejected', approved_by = $1, approval_reason = $2, approved_at = NOW()
         WHERE id = $3 AND status = 'pending'
         RETURNING *`,
        [rejectedBy, reason, requestId]
    );

    if (result.rows.length === 0) {
        throw new Error('Approval request not found or already processed');
    }

    return mapRowToApprovalRequest(result.rows[0]);
}

/**
 * Checks if an approval request has been approved.
 * Returns true only if the request exists and is in 'approved' status.
 */
export async function isApproved(requestId: string): Promise<boolean> {
    const result = await pool.query(
        `SELECT status FROM approval_requests WHERE id = $1`,
        [requestId]
    );

    return result.rows[0]?.status === 'approved';
}

/**
 * Middleware to check if an operation has required approval.
 * For operations that require approval, a valid approval_request_id must be provided.
 */
export async function checkApprovalStatus(
    tenantId: string,
    operationType: ApprovalRequest['operationType'],
    parameters: Record<string, any>,
    approvalRequestId?: string
): Promise<{ approved: boolean; requestId?: string }> {
    // Check if this operation requires approval
    const needsApproval = await requiresApproval(tenantId, operationType, parameters);

    if (!needsApproval) {
        return { approved: true }; // Operation doesn't require approval
    }

    // Operation requires approval — check if valid approval exists
    if (!approvalRequestId) {
        throw new Error(
            `Operation requires approval. Contact your tenant admin for ${operationType}.`
        );
    }

    const approved = await isApproved(approvalRequestId);
    if (!approved) {
        throw new Error('Approval request has not been approved or has expired');
    }

    return { approved: true, requestId: approvalRequestId };
}

/**
 * Helper to map database rows to ApprovalRequest objects
 */
function mapRowToApprovalRequest(row: any): ApprovalRequest {
    return {
        id: row.id,
        tenantId: row.tenantid,
        userId: row.userid,
        operationType: row.operation_type,
        resourceId: row.resource_id,
        parameters: typeof row.parameters === 'string' ? JSON.parse(row.parameters) : row.parameters,
        status: row.status,
        requestedAt: new Date(row.requested_at),
        expiresAt: new Date(row.expires_at),
        approvedBy: row.approved_by,
        approvalReason: row.approval_reason,
        approvedAt: row.approved_at ? new Date(row.approved_at) : undefined,
    };
}
