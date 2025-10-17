import type { NextConfig } from "next"

const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: "standalone", // Для Docker
  images: {
    formats: ["image/avif", "image/webp"],
  },
}

export default nextConfig
