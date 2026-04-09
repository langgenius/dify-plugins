// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { NextRequest, NextResponse } from "next/server";
import { BetaAnalyticsDataClient } from "@google-analytics/data";
import { getAdminAuth } from "@/lib/firebase-admin";

export const dynamic = "force-dynamic";

const PROPERTY_ID = "525946717";
const ADMIN_EMAILS_RAW = (process.env.ADMIN_EMAILS || process.env.NEXT_PUBLIC_ADMIN_EMAILS || "").split(",").map(e => e.trim()).filter(Boolean);
const ADMIN_EMAILS = ADMIN_EMAILS_RAW.length > 0 ? ADMIN_EMAILS_RAW : ["peghin@gmail.com"];

export async function GET(req: NextRequest) {
    try {
        // --- 1. Admin Auth ---
        const authHeader = req.headers.get("authorization");
        if (!authHeader?.startsWith("Bearer ")) {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
        }
        const token = authHeader.slice(7);
        let decodedToken: { email?: string };
        try {
            decodedToken = await getAdminAuth().verifyIdToken(token);
        } catch {
            return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
        }
        if (!decodedToken.email || !ADMIN_EMAILS.includes(decodedToken.email)) {
            return NextResponse.json({ error: "Forbidden" }, { status: 403 });
        }

        // --- 2. Initialize Analytics Client ---
        const analyticsDataClient = new BetaAnalyticsDataClient({
            credentials: {
                client_email: process.env.FIREBASE_CLIENT_EMAIL,
                private_key: process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, "\n"),
            },
        });

        // --- 3. Run Reports (Last 7 Days) ---
        // 3.1 Totals & Daily Stats
        const [response] = await analyticsDataClient.runReport({
            property: `properties/${PROPERTY_ID}`,
            dateRanges: [{ startDate: "7daysAgo", endDate: "today" }],
            dimensions: [{ name: "date" }],
            metrics: [
                { name: "activeUsers" },
                { name: "sessions" },
                { name: "screenPageViews" },
                { name: "averageSessionDuration" }
            ],
        });

        const dailyStats = response.rows?.map(row => ({
            date: row.dimensionValues?.[0]?.value,
            users: parseInt(row.metricValues?.[0]?.value || "0"),
            sessions: parseInt(row.metricValues?.[1]?.value || "0")
        })) || [];

        const totals = {
            users: dailyStats.reduce((acc, curr) => acc + curr.users, 0),
            sessions: dailyStats.reduce((acc, curr) => acc + curr.sessions, 0),
            pageviews: response.rows?.reduce((acc, row) => acc + parseInt(row.metricValues?.[2]?.value || "0"), 0) || 0,
            avgSessionDuration: response.rows?.[0] ? parseFloat(response.rows[0].metricValues?.[3]?.value || "0") : 0
        };

        // 3.2 Top Pages
        const [pagesResponse] = await analyticsDataClient.runReport({
            property: `properties/${PROPERTY_ID}`,
            dateRanges: [{ startDate: "7daysAgo", endDate: "today" }],
            dimensions: [{ name: "pagePath" }],
            metrics: [{ name: "screenPageViews" }],
            limit: 10
        });

        const topPages = pagesResponse.rows?.map(row => ({
            path: row.dimensionValues?.[0]?.value,
            views: parseInt(row.metricValues?.[0]?.value || "0")
        })) || [];

        // 3.3 Top Geos
        const [geosResponse] = await analyticsDataClient.runReport({
            property: `properties/${PROPERTY_ID}`,
            dateRanges: [{ startDate: "7daysAgo", endDate: "today" }],
            dimensions: [{ name: "country" }],
            metrics: [{ name: "activeUsers" }],
            limit: 5
        });

        const topGeos = geosResponse.rows?.map(row => ({
            country: row.dimensionValues?.[0]?.value,
            users: parseInt(row.metricValues?.[0]?.value || "0")
        })) || [];

        return NextResponse.json({
            totals,
            dailyStats: dailyStats.sort((a, b) => (a.date || "").localeCompare(b.date || "")),
            topPages,
            topGeos
        });

    } catch (err: any) {
        console.error("[GA4 Data API] Error:", err.message);
        return NextResponse.json({ 
            error: "Failed to fetch GA4 metrics", 
            message: err.message,
            propertyId: PROPERTY_ID 
        }, { status: 500 });
    }
}
