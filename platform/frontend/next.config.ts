import type { NextConfig } from "next";

const config: NextConfig = {
  output: "standalone",
  devIndicators: false,
  async rewrites() {
    const apiUrl = process.env.API_URL ?? "http://localhost:8000";
    return [
      {
        source: "/api/:path*",
        destination: `${apiUrl}/api/:path*`,
      },
    ];
  },
};

export default config;
