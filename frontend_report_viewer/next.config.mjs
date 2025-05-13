/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // If your reports (JSON and images) are served from the same domain
  // under the `public` folder or via API routes, you might not need specific
  // image remote patterns. If they are on a different domain, configure here.
  // images: {
  //   remotePatterns: [
  //     {
  //       protocol: 'https',
  //       hostname: 'example.com',
  //       port: '',
  //       pathname: '/images/**',
  //     },
  //   ],
  // },
};

export default nextConfig;
