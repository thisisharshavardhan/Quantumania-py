/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}"
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: { "2xl": "1400px" }
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        // Softer dark theme (near-slate) for better contrast without harsh black
    background: "var(--color-background)",
    foreground: "var(--color-foreground)",
    primary: { DEFAULT: "var(--color-primary)", foreground: "var(--color-primary-foreground)" },
    secondary: { DEFAULT: "var(--color-secondary)", foreground: "var(--color-secondary-foreground)" },
    destructive: { DEFAULT: "var(--color-destructive)", foreground: "var(--color-destructive-foreground)" },
    muted: { DEFAULT: "var(--color-muted)", foreground: "var(--color-muted-foreground)" },
    accent: { DEFAULT: "var(--color-accent)", foreground: "var(--color-accent-foreground)" },
    popover: { DEFAULT: "var(--color-popover)", foreground: "var(--color-popover-foreground)" },
    card: { DEFAULT: "var(--color-card)", foreground: "var(--color-card-foreground)" },
    border: "var(--color-border)",
    input: "var(--color-input)",
    ring: "var(--color-ring)",
    elevation: { 1: 'var(--color-elevation-1)', 2: 'var(--color-elevation-2)', 3: 'var(--color-elevation-3)' }
      },
      borderRadius: { lg: "12px", md: "10px", sm: "8px" },
      keyframes: { 'fade-in': { '0%': { opacity: 0 }, '100%': { opacity: 1 } } },
      animation: { 'fade-in': 'fade-in 0.3s ease-in-out' }
    }
  },
  plugins: [],
}
