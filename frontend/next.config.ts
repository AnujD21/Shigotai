import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Produces a self-contained server.js + minimal node_modules, which is
  // what frontend/Dockerfile builds against. Vercel ignores this and uses
  // its own build pipeline, so it's harmless if you deploy there instead.
  output: "standalone",
};

export default nextConfig;
