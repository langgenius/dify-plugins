// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import type { NextConfig } from "next";
import path from "path";

import { SLUG_MAP } from "./src/i18n/slug-map";

const nextConfig: NextConfig = {
  // Tell Next.js/Turbopack to NEVER bundle these packages — load them via
  // Node.js native require() at runtime on the server instead. This is the
  // correct fix for grpc/firebase-admin transitive dependency leakage.
  serverExternalPackages: [
    'firebase-admin',
    '@google-cloud/firestore',
    '@google-cloud/storage',
    '@grpc/grpc-js',
    '@grpc/proto-loader',
    'google-gax',
    'google-auth-library',
    '@google/genai',
    '@google-analytics/data',
    'protobufjs',
    'pg',
    'pg-native',
    'sqlite3',
  ],
  async rewrites() {
    const routes: any[] = [];
    for (const [internalSlug, mapping] of Object.entries(SLUG_MAP)) {
      for (const [locale, publicSlug] of Object.entries(mapping)) {
        routes.push({
          source: `/${locale}/${publicSlug}`,
          destination: `/${locale}/${internalSlug}`
        });
      }
    }
    return routes;
  },
  async redirects() {
    return [
      {
        source: '/login',
        destination: '/en/login',
        permanent: false,
      },
      {
        source: '/admin/:path*',
        destination: '/en/admin/:path*',
        permanent: false,
      },
      {
        source: '/dashboard/:path*',
        destination: '/en/dashboard/:path*',
        permanent: false,
      },
      {
        source: '/beta',
        destination: '/en/beta',
        permanent: false,
      }
    ];
  },
  async headers() {
    return [
      {
        // Noindex all Vercel preview/staging deployments to prevent duplicate indexation
        source: '/(.*)',
        headers: [
          {
            key: 'X-Robots-Tag',
            value: 'noindex',
          },
        ],
        // Only apply when served from the Vercel preview domain
        has: [
          {
            type: 'host',
            value: '(?!www\\.supra-wall\\.com).*\\.vercel\\.app',
          },
        ],
      },
    ];
  },
  transpilePackages: [
    "react-remove-scroll",
    "use-sync-external-store",
    "web-streams-polyfill"
  ],
  webpack: (config, { isServer }) => {
    // For client bundles: stub out any Node.js-only modules that may be
    // transitively referenced but never actually executed on the client.
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        pg: false,
        sqlite3: false,
        "firebase-admin": false,
        "@grpc/grpc-js": false,
        "grpc": false,
        net: false,
        tls: false,
        fs: false,
        dns: false,
        crypto: false,
        path: false,
        os: false,
        stream: false,
        constants: false,
        http2: false,
        zlib: false,
        child_process: false,
      };
    }
    return config;
  },
  turbopack: {
    resolveAlias: {
      // Force recharts to use its CJS lib bundle (avoids ESM d3-shape → d3-path issue)
      recharts: "recharts/lib/index.js",
      "web-streams-polyfill/dist/ponyfill.es2018.js": "web-streams-polyfill/dist/ponyfill.js",
    },
  },
};

export default nextConfig;
