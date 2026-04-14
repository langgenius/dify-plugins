// Copyright 2026 SupraWall Contributors
// SPDX-License-Identifier: Apache-2.0

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { i18n } from './i18n/config';

/**
 * Get the locale from request headers.
 */
function getLocale(request: NextRequest): string {
  const acceptLanguage = request.headers.get('accept-language');
  if (!acceptLanguage) return i18n.defaultLocale;

  const languages = acceptLanguage.split(',').map((lang) => {
    const [tag] = lang.split(';q=');
    return tag.trim().split('-')[0].toLowerCase();
  });

  const matched = languages.find((lang) => 
    i18n.locales.includes(lang as any)
  );

  return matched || i18n.defaultLocale;
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Check if there is any supported locale in the pathname
  const pathnameHasLocale = i18n.locales.some(
    (locale) => pathname.startsWith(`/${locale}/`) || pathname === `/${locale}`
  );

  if (pathnameHasLocale) return;

  // Redirect if there is no locale
  const locale = getLocale(request);
  
  // Create a new URL for the redirect
  const url = new URL(request.url);
  url.pathname = `/${locale}${pathname === '/' ? '' : pathname}`;
  
  return NextResponse.redirect(url, 307);
}

export const config = {
  matcher: [
    // Skip all internal paths (_next, static)
    // Skip static files (images, favicon, robots.txt, etc.)
    // Skip API routes
    // Skip internal dashboard area logic (which should handle its own session)
    // BUT INCLUDE login and admin/login to handle the root-level redirect to [lang]
    '/((?!api|dashboard|share|_next/static|_next/image|favicon.ico|robots.txt|sitemap.xml|og-image.png|.*\\..*).*)',
  ],
};
