import type { NextConfig } from "next";

const nextConfig: NextConfig = {
    // ...other Next.js configuration options

    typescript: {
        ignoreBuildErrors: true, // This ignores TypeScript errors during build
    },

    eslint: {
        // This ignores ESLint errors during `npm run build`
        ignoreDuringBuilds: true,
    },
};

export default nextConfig;
