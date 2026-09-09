"use client";

import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";
import {
  CircleAlert,
  LayoutDashboard,
  Lightbulb,
  ListChecks,
  Settings,
} from "lucide-react";

const NAV = [
  { href: "/", label: "Panoramica", icon: LayoutDashboard },
  { href: "/exceptions", label: "Coda di review", icon: ListChecks, countKey: "openCount" as const },
  { href: "/insights", label: "Analisi", icon: CircleAlert },
  { href: "/improvements", label: "Miglioramenti", icon: Lightbulb, countKey: "improvementCount" as const },
];

type AppShellProps = {
  children: React.ReactNode;
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
  openCount?: number;
  improvementCount?: number;
  back?: { href: string; label: string };
};

export function AppShell({
  children,
  title,
  subtitle,
  actions,
  openCount = 0,
  improvementCount = 0,
  back,
}: AppShellProps) {
  const pathname = usePathname();
  const search = useSearchParams();
  const counts = { openCount, improvementCount };

  return (
    <div className="min-h-screen bg-surface-app text-ink-950">
      <aside className="fixed inset-y-0 left-0 z-20 flex w-56 flex-col border-r border-line bg-white">
        <div className="flex items-center gap-3 px-5 py-5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-lime text-sm font-bold text-ink-950">
            P
          </div>
          <div>
            <div className="text-sm font-semibold leading-tight">Payroll Ops</div>
            <div className="text-[11px] font-medium uppercase tracking-[0.14em] text-ink-500">
              Console operativa
            </div>
          </div>
        </div>
        <nav className="mt-2 flex-1 space-y-1 px-3">
          {NAV.map((item) => {
            const active = item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
            const Icon = item.icon;
            const count = item.countKey ? counts[item.countKey] : undefined;
            const href = search.get("batch") ? `${item.href}?batch=${search.get("batch")}` : item.href;
            return (
              <Link
                key={item.href}
                href={href}
                className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-colors ${
                  active
                    ? "bg-lime-soft font-semibold text-ink-950"
                    : "font-medium text-ink-650 hover:bg-surface-muted hover:text-ink-950"
                }`}
              >
                <Icon size={18} strokeWidth={1.85} />
                <span className="flex-1">{item.label}</span>
                {typeof count === "number" && count > 0 ? (
                  <span className="rounded-full bg-white px-2 py-0.5 text-[11px] font-semibold text-ink-800 ring-1 ring-line">
                    {count}
                  </span>
                ) : null}
              </Link>
            );
          })}
        </nav>
        <div className="border-t border-line px-5 py-4">
          <div className="flex items-center gap-2 text-sm text-ink-500">
            <Settings size={16} strokeWidth={1.85} />
            Impostazioni
          </div>
          <p className="mt-3 text-[11px] leading-relaxed text-ink-500">
            Dati demo sintetici. Le regole sono deterministiche. L&apos;AI non può risolvere il payroll.
          </p>
        </div>
      </aside>
      <div className="pl-56">
        <header className="flex items-start justify-between gap-6 px-8 pb-2 pt-7">
          <div>
            {back ? (
              <Link href={back.href} className="mb-2 inline-block text-sm font-semibold text-ink-650">
                ← {back.label}
              </Link>
            ) : null}
            <h1 className="text-[28px] font-bold leading-tight tracking-tight">{title}</h1>
            {subtitle ? <p className="mt-1 text-sm text-ink-650">{subtitle}</p> : null}
          </div>
          {actions}
        </header>
        <main className="px-8 pb-10 pt-4">{children}</main>
      </div>
    </div>
  );
}
