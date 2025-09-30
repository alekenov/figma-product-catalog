/**
 * Cvety.kz Customer Website Worker
 * Serves static React SPA with client-side routing support
 * SPA routing is handled by wrangler.toml: not_found_handling = "single-page-application"
 */

export default {
  async fetch(request, env, ctx) {
    // Let Cloudflare handle SPA routing automatically
    return env.ASSETS.fetch(request);
  },
};