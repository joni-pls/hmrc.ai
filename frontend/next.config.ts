import type { NextConfig } from "next";

const nextConfig: NextConfig = {

  // Ensure the build output is a standalone app, which is what Vercel prefers.
  output: 'standalone',
};

export default nextConfig;
