import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Appota Knowledge Guard — Trợ lý chính sách',
  description: 'Trợ lý tra cứu chính sách nhân sự nội bộ với kiểm soát quyền truy cập và dẫn chứng nguyên văn.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
      </head>
      <body>{children}</body>
    </html>
  );
}
