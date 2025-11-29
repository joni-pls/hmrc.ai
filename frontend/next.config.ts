import type { NextConfig } from "next";

const nextConfig: NextConfig = {

    basePath: process.env.NODE_ENV === 'production' ? '' : '/frontend',

  // Ensure the build output is a standalone app, which is what Vercel prefers.
  output: 'standalone',
};

export default nextConfig;
