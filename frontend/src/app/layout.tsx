import type { Metadata } from "next";
import { IBM_Plex_Sans, IBM_Plex_Sans_JP, Noto_Serif_JP } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";
import { SITE_URL } from "@/lib/site";

const plexSans = IBM_Plex_Sans({
  variable: "--font-plex-sans",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  display: "swap",
});

const plexSansJP = IBM_Plex_Sans_JP({
  variable: "--font-plex-sans-jp",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  display: "swap",
});

// Mincho-style display face for headlines. It covers Latin and Japanese in
// one family, so a heading like "東京 · Tokyo" never mixes two serifs.
const notoSerifJP = Noto_Serif_JP({
  variable: "--font-noto-serif-jp",
  subsets: ["latin"],
  weight: ["500", "600", "700"],
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: "Shigotai — Find the Japanese jobs that fit you",
    template: "%s — Shigotai",
  },
  description:
    "Shigotai analyzes your skills, Japanese ability, education and experience to find currently active opportunities at Japanese companies.",
  openGraph: {
    title: "Shigotai — Find the Japanese jobs that fit you",
    description:
      "Shigotai analyzes your skills, Japanese ability, education and experience to find currently active opportunities at Japanese companies.",
    siteName: "Shigotai",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Shigotai — Find the Japanese jobs that fit you",
    description: "AI-powered career intelligence for Japan-focused job seekers.",
  },
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${plexSans.variable} ${plexSansJP.variable} ${notoSerifJP.variable} h-full`}
      // Smooth scrolling is for in-page anchors; this tells Next.js 16 to keep
      // route changes jumping instantly to the top.
      data-scroll-behavior="smooth"
      suppressHydrationWarning
    >
      <body className="min-h-full flex flex-col font-sans antialiased">
        <a href="#main-content" className="skip-link">
          Skip to content
        </a>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
