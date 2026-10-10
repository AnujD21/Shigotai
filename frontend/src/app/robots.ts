import type { MetadataRoute } from "next";
import { SITE_URL } from "@/lib/site";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: {
      userAgent: "*",
      allow: ["/", "/jobs", "/companies", "/how-it-works", "/about", "/login", "/register"],
      disallow: [
        "/dashboard",
        "/matches",
        "/profile",
        "/saved",
        "/notifications",
        "/settings",
        "/verify-email",
        "/reset-password",
      ],
    },
    sitemap: `${SITE_URL}/sitemap.xml`,
  };
}
