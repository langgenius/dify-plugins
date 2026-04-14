// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

type LogLevel = 'DEBUG' | 'INFO' | 'WARN' | 'ERROR';

class Logger {
    private isProduction = process.env.NODE_ENV === 'production';

    private static readonly KEYS_TO_SCRUB = [
        'apikey', 'agentapikey', 'secret', 'password', 'token',
        'authorization', 'credentials', 'vault_key', 'private_key',
        'client_secret', 'access_token', 'refresh_token'
    ];

    private scrubMeta(meta: any, seen?: WeakSet<object>): any {
        if (!meta || typeof meta !== 'object') return meta;

        // Circular reference guard
        const visited = seen || new WeakSet();
        if (visited.has(meta)) return '[Circular]';
        visited.add(meta);

        if (Array.isArray(meta)) {
            return meta.map(item => this.scrubMeta(item, visited));
        }

        const scrubbed = { ...meta };
        for (const key of Object.keys(scrubbed)) {
            const lowerKey = key.toLowerCase();
            if (Logger.KEYS_TO_SCRUB.some(k => lowerKey.includes(k))) {
                scrubbed[key] = '[REDACTED]';
            } else if (scrubbed[key] !== null && typeof scrubbed[key] === 'object') {
                scrubbed[key] = this.scrubMeta(scrubbed[key], visited);
            }
        }
        return scrubbed;
    }

    private formatMessage(level: LogLevel, message: string, meta?: any) {
        const timestamp = new Date().toISOString();
        const scrubbedMeta = this.scrubMeta(meta);
        const payload = {
            timestamp,
            level,
            message,
            ...scrubbedMeta
        };

        if (this.isProduction) {
            return JSON.stringify(payload);
        }

        // Pretty print for development
        const color = level === 'ERROR' ? '\x1b[31m' : level === 'WARN' ? '\x1b[33m' : '\x1b[32m';
        return `[${timestamp}] ${color}${level}\x1b[0m: ${message} ${scrubbedMeta ? JSON.stringify(scrubbedMeta) : ''}`;
    }

    debug(message: string, meta?: any) {
        if (!this.isProduction) {
            console.debug(this.formatMessage('DEBUG', message, meta));
        }
    }

    info(message: string, meta?: any) {
        console.info(this.formatMessage('INFO', message, meta));
    }

    warn(message: string, meta?: any) {
        console.warn(this.formatMessage('WARN', message, meta));
    }

    error(message: string, meta?: any) {
        console.error(this.formatMessage('ERROR', message, meta));
    }
}

export const logger = new Logger();
