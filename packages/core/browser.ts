// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

// This is a browser-safe version of the SupraWall core.
// It excludes database adapters that require Node.js modules like 'pg', 'net', or 'tls'.

import { SupraWallConfig, Adapter, Agent } from "./types";
import { SupabaseAdapter } from "./adapters/supabase";
import { FirebaseAdapter } from "./adapters/firebase";

export class SupraWall {
    private adapter: Adapter | null = null;
    private _connectionPromise: Promise<void> | null = null;

    async config(config: SupraWallConfig) {
        switch (config.adapter) {
            case "supabase":
                this.adapter = new SupabaseAdapter();
                break;
            case "firebase":
                this.adapter = new FirebaseAdapter();
                break;
            default:
                throw new Error(`Adapter ${config.adapter} is not supported in the browser. Use a server-side entry point for SQL/Mongo adapters.`);
        }

        if (config.connectionString && this.adapter) {
             this._connectionPromise = this.adapter.connect(config.connectionString);
        }
    }

    async init(): Promise<void> {
        if (this._connectionPromise) await this._connectionPromise;
    }

    __interop_setAdapterDb(db: any) {
        if (this.adapter && 'setDb' in this.adapter) {
            (this.adapter as any).setDb(db);
        }
    }

    get agents() {
        if (!this.adapter) throw new Error("SupraWall is not configured.");
        const adapter = this.adapter;
        return {
            create: async (agent: Agent) => adapter.createAgent(agent),
            get: async (id: string) => adapter.getAgent(id),
            update: async (id: string, updates: Partial<Agent>) => adapter.updateAgent(id, updates),
            delete: async (id: string) => adapter.deleteAgent(id),
            list: async (filter?: { userId?: string }) => adapter.listAgents(filter),
        };
    }
}

export const suprawall = new SupraWall();

export * from "./types";
export * from "./semantic";
export * from "./vault";
export * from "./src/templates/types";
export * from "./src/templates/baseline-controls";
export * from "./src/templates/sector-templates";
