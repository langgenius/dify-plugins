// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { Metadata } from "next";
import { Navbar } from "@/components/Navbar";
import { i18n, Locale } from "@/i18n/config";
import { SLUG_MAP } from "../../../i18n/slug-map";
import ComplianceClient from "./ComplianceClient";

export async function generateMetadata({ params }: { params: Promise<{ lang: string }> }): Promise<Metadata> {
    const { lang } = await params;
    const baseUrl = 'https://www.supra-wall.com';
    const isDefault = lang === i18n.defaultLocale;
    const internalSlug = 'compliance';

    // Build alternates for hreflang pointing to public aliases
    const languages: Record<string, string> = {};
    i18n.locales.forEach((l) => {
        const publicSlug = SLUG_MAP[internalSlug]?.[l] || internalSlug;
        languages[l] = `${baseUrl}/${l}/${publicSlug}`;
    });
    const defaultPublicSlug = SLUG_MAP[internalSlug]?.['en'] || internalSlug;
    languages['x-default'] = `${baseUrl}/en/${defaultPublicSlug}`;

    const currentPublicSlug = SLUG_MAP[internalSlug]?.[lang] || internalSlug;

    return {
        title: "Enterprise AI Compliance Framework | EU AI Act & HIPAA | SupraWall",
        description: "The complete compliance stack for autonomous systems. Zero-trust runtime security, deterministic audit logs, and risk controls for the EU AI Act.",
        alternates: {
            canonical: `${baseUrl}/${lang}/${currentPublicSlug}`,
            languages,
        },
        robots: {
            index: true,
            follow: true,
        },
    };
}

import { getDictionary } from "../../../i18n/getDictionary";

export default async function Page({
    params,
}: {
    params: Promise<{ lang: string }>;
}) {
    const { lang } = (await params) as { lang: Locale };
    const dictionary = await getDictionary(lang);
    const jsonLd = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": "SupraWall Compliance Framework",
        "description": "Enterprise-grade security and compliance for autonomous AI agents.",
        "url": `https://www.supra-wall.com/${lang}/compliance`,
        "inLanguage": lang,
        "publisher": {
            "@type": "Organization",
            "name": "SupraWall",
            "logo": {
                "@type": "ImageObject",
                "url": "https://www.supra-wall.com/logo.png"
            }
        }
    };

    return (
        <div className="min-h-screen bg-black">
            <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
            <Navbar lang={lang} dictionary={dictionary} />
            <ComplianceClient dictionary={dictionary} lang={lang} />
        </div>
    );
}
