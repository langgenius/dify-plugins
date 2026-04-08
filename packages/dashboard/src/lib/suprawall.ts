// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

/**
 * CLIENT-SAFE MOCK
 * This file replaces the real suprawall initialization during client-side bundling.
 * It prevents the bundler from following imports into the @suprawall/core package
 * which may transitively pull in Node.js-only modules like 'pg' or 'firebase-admin'.
 */

export const suprawall: any = {
    config: () => { console.warn("SupraWall: config() called on client-side mock. Initialization skipped."); },
    registerAdapter: () => {},
    agents: {
        create: async () => { throw new Error("SupraWall: agents.create() is not available on the client-side."); },
        get: async () => { throw new Error("SupraWall: agents.get() is not available on the client-side."); },
        update: async () => { throw new Error("SupraWall: agents.update() is not available on the client-side."); },
        delete: async () => { throw new Error("SupraWall: agents.delete() is not available on the client-side."); },
        list: async () => { throw new Error("SupraWall: agents.list() is not available on the client-side."); },
    }
};

export class SupabaseAdapter {}
export class FirebaseAdapter {}
