import type { Metadata } from "next";
import { Montserrat } from "next/font/google";
import { Suspense } from "react";
import "./globals.css";

const montserrat = Montserrat({
  subsets: ["latin"],
  variable: "--font-sans",
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "Payroll Ops Workbench",
  description: "Deterministic payroll exception review with human resolution and operations insights.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={montserrat.variable}>
        <Suspense fallback={<div className="p-8 text-sm text-ink-500">Loading…</div>}>{children}</Suspense>
      </body>
    </html>
  );
}
