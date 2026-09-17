import { Analytics } from '@vercel/analytics/next'
import type { Metadata, Viewport } from 'next'
import './globals.css'

/**
 * Global site metadata configuration for SEO and search crawlers.
 */
export const metadata: Metadata = {
  title: 'Vibelnyc - Find Tracks By Sonic DNA',
  description: 'Discover music that matches your sonic DNA with Vibelnyc.',
  generator: 'v0.app',
  icons: {
    icon: [
      {
        url: '/icon-light-32x32.png',
        media: '(prefers-color-scheme: light)',
      },
      {
        url: '/icon-dark-32x32.png',
        media: '(prefers-color-scheme: dark)',
      },
      {
        url: '/icon.svg',
        type: 'image/svg+xml',
      },
    ],
    apple: '/apple-icon.png',
  },
}

/**
 * Responsive viewport and device theme configuration.
 */
export const viewport: Viewport = {
  colorScheme: 'light dark',
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: 'white' },
    { media: '(prefers-color-scheme: dark)', color: 'black' },
  ],
}

/**
 * Root application layout wrapper configuring html, body font styling, and analytics.
 *
 * @param props Contains children React nodes to render within the document shell.
 * @returns JSX Element rendering the root HTML tree.
 */
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
        {process.env.NODE_ENV === 'production' && <Analytics />}
      </body>
    </html>
  )
}
