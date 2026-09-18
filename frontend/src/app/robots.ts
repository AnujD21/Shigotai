import type { MetadataRoute } from "next";

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
    sitemap: "https://shigotai.app/sitemap.xml",
  };
}
