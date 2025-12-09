import type { Metadata } from "next";
import { NextIntlClientProvider } from 'next-intl';
import { getLocale, getMessages } from 'next-intl/server';
import { Inter } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/providers/theme-provider";
import { AccessibilityProvider } from "@/hooks/use-accessibility";
import { Toaster } from "@/components/ui/toaster";
import { SkipLink } from "@/components/shared/SkipLink";
import { AccessibilityPanel } from "@/components/shared/AccessibilityPanel";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "AI Orchestra Gateway",
  description: "High-security AI orchestration middleware with privacy controls",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const locale = await getLocale();
  const messages = await getMessages();

  return (
    <html lang={locale} suppressHydrationWarning>
      <body className={inter.className}>
        <NextIntlClientProvider messages={messages}>
          <AccessibilityProvider>
            <ThemeProvider
              attribute="class"
              defaultTheme="system"
              enableSystem
              disableTransitionOnChange
            >
              <SkipLink />
              <main id="main-content">
                {children}
              </main>
              <Toaster />
              <AccessibilityPanel />
            </ThemeProvider>
          </AccessibilityProvider>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
