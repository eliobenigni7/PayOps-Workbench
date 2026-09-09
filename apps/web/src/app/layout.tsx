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
  title: "Payroll Ops — Console operativa",
  description: "Review deterministica delle eccezioni payroll, con risoluzione umana e analisi operative.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="it">
      <body className={montserrat.variable}>
        <Suspense fallback={<div className="p-8 text-sm text-ink-500">Caricamento…</div>}>{children}</Suspense>
      </body>
    </html>
  );
}
