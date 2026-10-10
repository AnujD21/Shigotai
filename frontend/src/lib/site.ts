/** Public origin of the site, used for absolute URLs (sitemap, robots, OG
 * images). Set NEXT_PUBLIC_SITE_URL on each deployment -- e.g. the
 * *.vercel.app URL until a custom domain is attached. */
export const SITE_URL = (process.env.NEXT_PUBLIC_SITE_URL ?? "https://shigotai.app").replace(/\/$/, "");
