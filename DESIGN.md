# DESIGN.md — Payroll Ops Workbench

## 0. Purpose

This file defines the visual and interaction system for Payroll Ops Workbench.

The target is **not** to clone Jet HR pixel-for-pixel. The target is to build an internal product that feels naturally adjacent to the current Jet HR product and public brand language: simple, direct, high-trust, product-first, operational, and unmistakably modern without looking like a generic "AI dashboard".

The visual reference comes from Jet HR's current public website, careers pages, press materials and public product imagery as reviewed in September 2026. Jet HR provides official logo/identity guidelines and product screenshots through its press area; this project deliberately does not bundle those proprietary assets.

**Rule:** if a design decision makes the interface look more impressive but makes the operator slower, remove it.

---

# 1. Visual character

The UI should communicate five things immediately:

1. **Clarity** — payroll operations are already complex; the interface must not be.
2. **Speed** — actions are obvious and close to the information that justifies them.
3. **Trust** — numbers, states and automated decisions are explainable.
4. **Personality** — use a sharp lime accent and confident typography, but no decorative excess.
5. **Product maturity** — this should look like a real internal tool, not a hackathon demo.

A useful shorthand:

> **Clean SaaS + operational density + lime confidence.**

Do not make it "futuristic". Do not make AI the visual protagonist.

---

# 2. What to borrow from Jet HR's design language

## 2.1 High-contrast typography

Jet HR's public surfaces use strong, compact headings, short copy blocks and clear hierarchy. The interface should therefore use:

- large but not oversized page titles;
- medium-to-heavy heading weights;
- compact labels;
- body copy with generous line-height;
- restrained use of uppercase for eyebrow labels and table metadata.

The tone should feel confident rather than corporate.

## 2.2 Bright green as an accent, not wallpaper

The recognisable Jet-style green/lime should be used for:

- primary actions;
- active navigation states;
- selected controls;
- success/progress accents;
- small emphasis surfaces;
- key metric highlights.

It should **not** cover the whole screen.

## 2.3 White / near-white product surfaces

The product should mostly live on:

- off-white application background;
- white cards / panels;
- subtle grey borders;
- near-black text.

Depth comes from borders, grouping and whitespace — not heavy shadows.

## 2.4 Rounded but disciplined components

Use medium radii. Jet HR feels approachable, but not toy-like.

Recommended:

- controls: `8px`;
- cards: `12px`;
- large panels / drawers: `16px`;
- pills/badges: fully rounded only where semantically appropriate.

## 2.5 Product screenshots over illustration aesthetics

For this project, data itself is the visual language. Use:

- tables;
- metric cards;
- status chips;
- inline charts;
- structured detail panels;
- progress bars;
- timelines.

Avoid decorative 3D illustrations, abstract blobs, AI gradients or stock people.

---

# 3. Design tokens

> The values below are **Jet HR-inspired implementation tokens**, not claimed to be official brand tokens. If this prototype is ever used with permission as an actual Jet HR artifact, replace them with values from the official brand kit.

## 3.1 Color palette

```css
:root {
  /* Brand-inspired */
  --brand-lime: #D8FF3E;
  --brand-lime-hover: #C9F52E;
  --brand-lime-soft: #F3FFD0;

  /* Neutrals */
  --ink-950: #111111;
  --ink-800: #2A2A28;
  --ink-650: #555550;
  --ink-500: #777770;
  --surface-app: #F6F6F2;
  --surface-card: #FFFFFF;
  --surface-muted: #F1F1EC;
  --border-default: #E3E3DC;
  --border-strong: #CFCFC5;

  /* Operational semantics */
  --critical: #D92D20;
  --critical-soft: #FFF0EE;
  --high: #E9711C;
  --high-soft: #FFF3E8;
  --medium: #B58800;
  --medium-soft: #FFF8D6;
  --info: #2563EB;
  --info-soft: #EEF4FF;
  --success: #19703A;
  --success-soft: #EAF7EE;
}
```

### Color rules

- **Lime is brand/action, not risk.** Never use lime to mean "safe" if it could be confused with a CTA.
- Risk colors appear primarily as text, dots, slim left borders and small badges.
- Avoid fully saturated red/orange cards.
- Use semantic color **plus text/icon**, never color alone.
- Large body copy is always near-black, never grey-on-grey.

---

# 4. Typography

Use **Montserrat** as the first visual approximation for the Jet HR-inspired direction, with `Inter` or the system sans stack as a robust fallback.

```css
font-family: "Montserrat", "Inter", ui-sans-serif, system-ui, -apple-system,
             BlinkMacSystemFont, "Segoe UI", sans-serif;
```

Do not ship proprietary font files in the repository.

## Type scale

| Token | Size | Weight | Usage |
|---|---:|---:|---|
| `display` | 32px | 700 | rare dashboard headline |
| `h1` | 28px | 700 | page title |
| `h2` | 20px | 650–700 | section title |
| `h3` | 16px | 650 | card title |
| `body` | 14px | 400–500 | primary UI copy |
| `small` | 12px | 500 | metadata |
| `label` | 11px | 650 | uppercase eyebrow / table meta |

Recommended line heights:

- headings: `1.15–1.25`;
- body: `1.45–1.55`;
- dense table cells: `1.25–1.35`.

### Numbers

Operational numbers matter. Enable tabular numerals where possible:

```css
font-variant-numeric: tabular-nums;
```

Large KPIs should be visually strong but not huge marketing counters.

---

# 5. Spacing and geometry

Base spacing unit: **4px**.

Core scale:

```text
4 / 8 / 12 / 16 / 20 / 24 / 32 / 40 / 48
```

Preferred component values:

- input height: `40px`;
- compact button: `36px`;
- default button: `40px`;
- table row: `48–56px`;
- card padding: `20–24px`;
- page gutter desktop: `28–32px`;
- sidebar width: `224–240px`;
- max content width: none for operational tables; constrain detail prose instead.

---

# 6. App shell

The application is an **internal operations tool**, so the product shell should dominate over a website-like layout.

## Desktop layout

```text
┌────────────────────────────────────────────────────────────────────┐
│  LEFT NAV          │  PAGE HEADER                                  │
│                    ├────────────────────────────────────────────────┤
│  Mark / product    │                                                │
│                    │  Page content                                  │
│  Overview          │                                                │
│  Review queue      │                                                │
│  Insights          │                                                │
│  Improvements      │                                                │
│                    │                                                │
│                    │                                                │
│  Settings          │                                                │
└────────────────────────────────────────────────────────────────────┘
```

### Sidebar

- white or near-white;
- 1px right border;
- no dark/navy sidebar;
- small product mark at top;
- active item uses a lime-tinted background and dark text;
- icons 18–20px, simple outline style;
- no icon gradients.

Example active navigation:

```text
[●] Overview
[ ] Review queue     93
[ ] Insights
[ ] Improvements      3
```

The count may use a neutral or lime badge, but avoid notification-red unless urgent.

### Top header

Keep it light. Page title on left; batch selector, search or relevant action on right.

Do not create a permanent giant top bar.

---

# 7. Screen 1 — Operations Control Center

This is the first portfolio screenshot and must be excellent.

## Header

```text
Operations Control Center
Payroll batch · September 2026

                                [ Import batch ]
```

Under the title, optionally show a compact health statement:

`Batch processed · 1,284 records · last updated 09:42`

## KPI row

Use 4 cards in one row on desktop.

```text
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ PROCESSED        │ │ AUTO-CLEARED     │ │ NEEDS REVIEW     │ │ CRITICAL         │
│ 1,284            │ │ 1,191            │ │ 93               │ │ 14               │
│                  │ │ 92.8%            │ │ 7.2%             │ │ +2 vs last batch │
└──────────────────┘ └──────────────────┘ └──────────────────┘ └──────────────────┘
```

### KPI styling

- white card;
- thin border;
- 12px radius;
- no drop shadow by default;
- label small/uppercase/grey;
- number 28–32px / bold;
- lime underline, dot or micro-accent on the strongest positive metric;
- critical card may use a small red dot, not a red background.

## Effort-saved callout

This is the one place where a lime surface can be large:

```text
Estimated manual effort avoided today
6h 42m

Based on baseline review assumptions                 View methodology →
```

Use `brand-lime-soft` or `brand-lime`, depending on readability.

## Main content grid

Left 2/3:

- review queue preview (5–7 rows).

Right 1/3:

- top exception causes;
- oldest unresolved cases;
- small trend or progress visualization.

No donut chart unless it genuinely improves comprehension. Prefer bars.

---

# 8. Screen 2 — Review Queue

The queue should look like a serious operational tool.

## Toolbar

```text
Review queue                                      93 open
[Search records…]  [Priority ▾] [Issue type ▾] [Assignee ▾]  [More filters]
```

Filters should be visually quiet.

## Table

Recommended columns:

| Column | Notes |
|---|---|
| Priority | dot + label; sortable |
| Employee | name or synthetic ID + team |
| Issue | short human-readable reason |
| Risk | numeric score, tabular |
| Exposure | optional € amount |
| Age | e.g. `2h`, `1d` |
| Assignee | avatar initials / name |
| Action | `Open` or chevron |

Do not put a big "AI" button in every row. If an explanation exists, use a small sparkle/spark icon with tooltip or expose AI only inside the detail view.

### Row behavior

- whole row is clickable;
- hover = subtle grey fill;
- selected = lime-soft outline/background;
- critical = 3px left border or red dot;
- rows remain readable at 100+ records.

---

# 9. Screen 3 — Exception Detail

This is the strongest demonstration of product judgment.

## Structure

```text
← Review queue

Salary anomaly                                      [Critical 96]
EMP-1042 · Engineering · September 2026

┌──────────────────────────────┐  ┌──────────────────────────────┐
│ What changed                 │  │ Priority breakdown           │
│ Gross salary        €6,140   │  │ Severity              +40    │
│ 6m average          €4,320   │  │ Financial exposure    +25    │
│ Difference           +42.1%  │  │ Rule confidence       +20    │
│                              │  │ Missing support event +15    │
└──────────────────────────────┘  │ Total                  100    │
                                  └──────────────────────────────┘

Triggered checks
[!] Salary variation > 30%
[!] Outside historical range
[!] No salary-change event found

AI-assisted investigation
...

Resolution
[ Confirm issue ] [ Mark as expected ] [ Request info ] [ Escalate ]
```

### Principle: "Why is this here?"

Every critical value should answer **why**.

The risk score cannot be a mysterious AI score. Show a deterministic contribution breakdown.

---

# 10. AI panel

AI is **secondary assistance** visually.

Do not use purple, gradients, glowing borders or a chatbot bubble aesthetic.

Recommended panel:

```text
AI-assisted investigation                         [78% confidence]

The increase is inconsistent with the employee's recent payroll history.
No corresponding salary-change event is present in the provided HR data.

Suggested checks
• Promotion or compensation change not synced
• One-off adjustment
• Duplicate allowance

Sources used: payroll history, HR events, current batch

AI suggestions are informational only. Final resolution requires operator confirmation.
```

Style:

- white or muted grey panel;
- tiny lime icon/accent;
- confidence badge neutral, not celebratory;
- evidence sources visible;
- disclaimer always present;
- no fake typing animation.

The product must feel safe even if the AI component is removed.

---

# 11. Resolution interaction

Actions should be strong and finite.

Primary resolution buttons are not all primary-color buttons. Use hierarchy:

- `Confirm issue` — dark/near-black primary;
- `Mark as expected` — secondary outline;
- `Request information` — secondary;
- `Escalate` — destructive/attention style only if semantically needed.

After choosing an outcome, open an inline form or right-side drawer.

Example:

```text
Mark as expected

Reason
( ) Salary increase
( ) One-off bonus
( ) Manual adjustment
( ) Data correction
( ) Other

Note (optional)
[                                                   ]

                         [Cancel] [Resolve case]
```

Resolution reason is required because the Insights layer depends on structured feedback.

---

# 12. Screen 4 — Insights

The design should feel closer to an operations review than a BI dashboard.

Hero question:

> **Where are we spending avoidable manual effort?**

Recommended modules:

### A. Top sources of manual review

Horizontal bar chart:

```text
Missing employee data     ███████████████ 31%
Salary discrepancies      ████████████    24%
Bonus anomalies           █████████       18%
Overtime issues           ███████         14%
Other                     ██████          13%
```

### B. Effort by issue type

Table with:

- occurrences;
- average handling time;
- monthly hours;
- false-positive rate;
- trend.

### C. Rule quality

Show rules with high false-positive rates. This communicates operational maturity: automation itself needs continuous improvement.

### D. Improvement opportunities

3 compact cards maximum, ranked by expected impact.

---

# 13. Screen 5 — Improvement Opportunity

Use a one-page operational business case.

```text
Missing bank information
High impact · Low implementation effort

47 cases / month
6.2 min avg handling time
4.9h manual effort / month

Root-cause hypothesis
Bank information is not mandatory at the point where employee onboarding is completed.

Suggested intervention
Add completeness validation before onboarding can be marked complete.

Expected effect
Reduce downstream bank-data exceptions by 70–90%.

Measure after release
• monthly exception count
• average handling time
• onboarding completion rate
```

Use lime for the impact/effort recommendation and call-to-action, not for every statistic.

---

# 14. Components

## Buttons

### Primary

```css
background: var(--ink-950);
color: white;
border-radius: 8px;
```

Use for consequential user actions.

### Brand action

```css
background: var(--brand-lime);
color: var(--ink-950);
```

Use for creation/import/positive forward actions, not destructive resolution.

### Secondary

White background, 1px border, dark text.

### Ghost

No border, subtle hover surface. Best for utility actions.

## Inputs

- white background;
- 1px default border;
- 8px radius;
- strong visible focus ring using dark + lime offset where practical;
- labels above inputs, not placeholder-only.

## Cards

Default:

```css
background: var(--surface-card);
border: 1px solid var(--border-default);
border-radius: 12px;
box-shadow: none;
```

Only drawers, popovers and modals should get elevation shadows.

## Badges

Small, content-sized, always text + optional dot.

Examples:

- `Critical`
- `High`
- `Needs review`
- `Auto-cleared`
- `AI available`

Avoid giant pill UI everywhere.

## Charts

- default bars/lines use neutral ink;
- use lime to highlight the focus series;
- semantic red only for errors/critical;
- gridlines extremely subtle;
- no rainbow categorical palettes;
- labels on chart > legend when possible.

---

# 15. Icons

Use one consistent outline icon set (e.g. Lucide).

Recommended stroke weight: `1.75–2px`.

Icons support recognition; they do not replace labels for important navigation or actions.

AI iconography should be subtle. One small sparkle mark is enough.

---

# 16. Motion

Motion should reinforce state changes.

Allowed:

- 120–180ms hover/focus transitions;
- 180–240ms drawers/modal entrance;
- subtle row state transition after resolution;
- count-up only if it does not delay comprehension.

Avoid:

- parallax;
- decorative entrance animations;
- floating cards;
- glowing AI effects;
- looping motion.

An internal payroll operator should be able to use the app all day without visual fatigue.

---

# 17. Accessibility

Minimum expectations:

- WCAG AA text contrast;
- visible focus states;
- keyboard navigable table/actions;
- semantic HTML table where appropriate;
- icon-only buttons require accessible names/tooltips;
- risk state never communicated by color only;
- reduced-motion support;
- minimum interactive target around 36–40px.

---

# 18. Responsive behavior

This is a desktop-first operational product.

## Desktop > 1280px

Full sidebar, complete table, side-by-side detail panels.

## Tablet 768–1279px

Sidebar collapses to icons/drawer; less important table columns hide; exception detail stacks.

## Mobile < 768px

Support basic review/detail/resolution, but do not optimize the entire analytics experience around mobile. Queue rows become structured cards.

The portfolio screenshots should be captured at **1440 × 900** or similar.

---

# 19. Copy style

Jet HR's public language is direct and practical. Mirror that.

Prefer:

- `93 cases need review`
- `Why is this critical?`
- `No salary-change event found`
- `4.9 hours of manual review per month`
- `Fix the source of this issue`

Avoid:

- `Leverage advanced artificial intelligence`
- `Unlock operational synergies`
- `AI-powered intelligent orchestration`
- `Next-generation payroll transformation`

UI copy should describe the user's reality, not the technology.

---

# 20. Empty, loading and error states

These screens are part of the design, not implementation leftovers.

## Empty queue

```text
No cases need review
Everything in this batch passed the current validation rules.
[View batch summary]
```

Do not use confetti.

## Loading

Use skeleton rows preserving table geometry. Avoid generic full-page spinners.

## Rule/API failure

Be specific:

```text
3 records could not be evaluated
The employee-history dataset was unavailable for these records.
[Retry] [Open affected records]
```

Never silently treat an evaluation failure as a clean case.

---

# 21. Portfolio screenshot checklist

The final repository README should eventually contain 4 screenshots:

1. **Operations Control Center** — instant concept comprehension.
2. **Review Queue** — real operational density.
3. **Critical Exception Detail** — explainability + human-in-the-loop.
4. **Insights / Improvement Opportunity** — proves this is Operations Excellence, not merely anomaly detection.

Use real-looking synthetic data. Avoid lorem ipsum.

---

# 22. Things that would make this look wrong

Do **not** implement:

- dark mode as the primary screenshot;
- glassmorphism;
- purple/blue AI gradients;
- huge gradient hero sections inside the app;
- excessive shadows;
- neon risk cards;
- rounded rectangles around every line of text;
- a chatbot taking 30% of the screen;
- meaningless dashboard charts;
- over-sized icons;
- decorative illustrations;
- microservice/network diagrams inside the UI;
- fake "AI is thinking" theatrics.

If it resembles a crypto dashboard, AI wrapper or Dribbble concept more than an operations tool, redesign it.

---

# 23. Acceptance test for the design

A reviewer should understand the product from the first screenshot in under 10 seconds:

> "Most records are cleared automatically. The risky ones are prioritized for people. The tool explains why, captures outcomes, and uses recurring exceptions to improve the process upstream."

If the first reaction is merely "nice dashboard", the design has failed.

---

# 24. Reference posture

Public references reviewed when writing this document:

- Jet HR main website — current product and marketing language;
- Jet HR Operations Excellence careers page — internal-tool/problem-solving framing;
- Jet HR Software Engineer careers page — product-first and low-overhead engineering philosophy;
- Jet HR press area — official identity/product-material availability.

This repository should remain visibly **independent and portfolio-oriented**. Do not use Jet HR's logo, imply endorsement, or label the UI as an official Jet HR product unless permission is obtained.
