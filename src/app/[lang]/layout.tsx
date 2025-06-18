import { allMessages } from '@/appRouterI18n';
import { LinguiClientProvider } from '@/components/LinguiClientProvider';
import { initLingui, PageLangParam } from '@/initLingui';
import { cn } from '@/lib/utils';
import { useLingui } from '@lingui/react/macro';
import { Analytics } from '@vercel/analytics/next';
import { Plus_Jakarta_Sans } from 'next/font/google';
import { PropsWithChildren } from 'react';
import { Toaster } from 'sonner';
import './globals.css';
import { PostHogProvider } from './providers';

export async function generateMetadata(props: PropsWithChildren<PageLangParam>) {
  const lang = (await props.params).lang
  initLingui(lang)

  const { t } = useLingui()
  return {
    title: t`Get The Facts About Government Spending`,
    description: t`Government spending shouldn't be a black box. We turn complex data into clear, non-partisan insights so every Canadian knows where their money goes.`,
    icons: [
      {
        url: '/favicon-96x96.png',
        type: 'image/png',
        sizes: '96x96'
      },
      {
        url: '/favicon.svg',
        type: 'image/svg+xml'
      },
      {
        url: '/favicon.ico',
        rel: 'shortcut icon'
      },
      {
        url: '/apple-touch-icon.png',
        rel: 'apple-touch-icon',
        sizes: '180x180'
      }
    ],
    manifest: '/site.webmanifest',
    appleWebApp: {
      title: 'CanadaSpends'
    },
  }
}



const plusJakartaSans = Plus_Jakarta_Sans({
  weight: ['600', '700'],
  subsets: ['latin'],
});

export default async function RootLayout({ children, params }: PropsWithChildren<PageLangParam>) {
  const lang = (await params).lang
  initLingui(lang)

  return (
    <html lang={lang}>
      <body className={cn('antialiased', plusJakartaSans.className)}>
        <PostHogProvider>
          <LinguiClientProvider
            initialLocale={lang}
            initialMessages={allMessages[lang]!}
          >
            {children}
            <Toaster position="top-right" richColors />
          </LinguiClientProvider>
        </PostHogProvider>
        <Analytics />
        {/* Simple Analytics Script */}
        <script async defer src="https://scripts.simpleanalyticscdn.com/latest.js"></script>
        <noscript><img src="https://queue.simpleanalyticscdn.com/noscript.gif" alt="" referrerPolicy="no-referrer-when-downgrade" /></noscript>
      </body>
    </html>
  );
}
