import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Stock Intelligence Platform",
  description:
    "Research, portfolio analytics, and investment-thesis intelligence for long-term investors.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full">{children}</body>
    </html>
  );
}

