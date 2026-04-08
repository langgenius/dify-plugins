// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { SupraWallConfig, Adapter, Agent } from "./types";

export class SupraWall {
    private configOptions: SupraWallConfig | null = null;
    private adapter: Adapter | null = null;
    private _connectionPromise: Promise<void> | null = null;
    private adapters = new Map<string, any>();

    /**
     * Registers a database adapter. This allows the core to remains driver-agnostic
     * and prevents bundlers from pulling in heavy Node.js-only drivers (like 'pg')
     * into browser bundles unless they are explicitly registered.
     */
    registerAdapter(name: string, AdapterClass: any) {
        this.adapters.set(name, AdapterClass);
    }

    async config(config: SupraWallConfig) {
        this.configOptions = config;

        const AdapterClass = this.adapters.get(config.adapter);
        if (!AdapterClass) {
            throw new Error(
                `Adapter "${config.adapter}" is not registered. ` +
                `Make sure to call suprawall.registerAdapter("${config.adapter}", AdapterClass) first.`
            );
        }

        this.adapter = new AdapterClass();

        if (config.connectionString && this.adapter) {
            this._connectionPromise = this.adapter.connect(config.connectionString).catch(err => {
                process.stderr.write(`[SupraWall] Failed to connect ${config.adapter} adapter: ${err}\n`);
                throw err;
            });
        }
    }

    /**
     * Explicit async initializer. Call this after config() to guarantee the
     * database connection is established before performing any operations.
     *
     * @example
     *   suprawall.config({ adapter: "postgres", connectionString: "..." });
     *   await suprawall.init(); // waits for the connection
     */
    async init(): Promise<void> {
        if (this._connectionPromise) {
            await this._connectionPromise;
        }
    }

    // Expose internal setter for test/interop
    __interop_setAdapterDb(db: any) {
        if (this.adapter && 'setDb' in this.adapter) {
            (this.adapter as any).setDb(db);
        }
    }

    get agents() {
        if (!this.adapter) {
            throw new Error("SupraWall is not configured. Call suprawall.config() first.");
        }
        const adapter = this.adapter;
        const ensureConnected = this._connectionPromise
            ? () => this._connectionPromise!
            : () => Promise.resolve();

        return {
            create: async (agent: Agent) => { await ensureConnected(); return adapter.createAgent(agent); },
            get: async (id: string) => { await ensureConnected(); return adapter.getAgent(id); },
            update: async (id: string, updates: Partial<Agent>) => { await ensureConnected(); return adapter.updateAgent(id, updates); },
            delete: async (id: string) => { await ensureConnected(); return adapter.deleteAgent(id); },
            list: async (filter?: { userId?: string }) => { await ensureConnected(); return adapter.listAgents(filter); },
        };
    }
}

import { FirebaseAdapter } from "./adapters/firebase";
import { SupabaseAdapter } from "./adapters/supabase";

export const suprawall = new SupraWall();
export { FirebaseAdapter, SupabaseAdapter };
export * from "./types";
export * from "./semantic";
export * from "./vault";
export * from "./src/templates/types";
export * from "./src/templates/baseline-controls";
export * from "./src/templates/sector-templates";
