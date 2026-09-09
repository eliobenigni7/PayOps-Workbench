/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        lime: {
          DEFAULT: "var(--brand-lime)",
          hover: "var(--brand-lime-hover)",
          soft: "var(--brand-lime-soft)",
        },
        ink: {
          950: "var(--ink-950)",
          800: "var(--ink-800)",
          650: "var(--ink-650)",
          500: "var(--ink-500)",
        },
        surface: {
          app: "var(--surface-app)",
          card: "var(--surface-card)",
          muted: "var(--surface-muted)",
        },
        line: {
          DEFAULT: "var(--border-default)",
          strong: "var(--border-strong)",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "Inter", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        drawer: "0 16px 40px rgba(17, 17, 17, 0.12)",
      },
    },
  },
  plugins: [],
};
