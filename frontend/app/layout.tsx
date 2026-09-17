import type { Metadata } from 'next';
import './globals.css';
import { AppShell } from '@/components/AppShell';

export const metadata: Metadata = {
  title: 'ReachOut SMB - AI Sales & Customer Assistant for Instagram & WhatsApp',
  description: 'Automate sales conversations, product recommendations, lead qualification, and orders across Instagram and WhatsApp with multilingual AI.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
