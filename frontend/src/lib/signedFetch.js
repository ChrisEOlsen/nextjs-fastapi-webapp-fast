import crypto from "crypto";

const EXPECTED_HMAC_SECRET = process.env.EXPECTED_HMAC_SECRET;
const DOMAIN = process.env.DOMAIN;
const API_PREFIX = process.env.API_PREFIX;
const BACKEND_URL = process.env.BACKEND_URL

if (!EXPECTED_HMAC_SECRET || !DOMAIN || !API_PREFIX) {
  const missing = [];
  if (!EXPECTED_HMAC_SECRET) missing.push('EXPECTED_HMAC_SECRET');
  if (!DOMAIN) missing.push('DOMAIN');
  if (!API_PREFIX) missing.push('API_PREFIX');
  throw new Error(`Missing required environment variables for signedFetch: ${missing.join(', ')}`);
}

/**
 * Generate a secure HMAC-SHA256 signature for a domain.
 * @param {string} domain
 * @returns {string} HMAC hex digest
 */
function generateTenantSignature(domain) {
  return crypto
    .createHmac("sha256", EXPECTED_HMAC_SECRET)
    .update(domain)
    .digest("hex");
}

/**
 * Secure server-side fetch to your FastAPI backend with signed tenant headers.
 * @param {string} path - Relative API path (e.g., "/google-client-credentials")
 * @param {object} req - The Next.js API or SSR request object
 * @param {object} options - Fetch options (optional)
 * @returns {Promise<Response>}
 */
export async function signedFetch(path, req, options = {}) {
  const domain = DOMAIN;
  const signature = generateTenantSignature(domain);

  const targetUrl = `http://${BACKEND_URL}${API_PREFIX}${path}`;

  const headers = {
    "Content-Type": "application/json",
    "X-Tenant-Domain": domain,
    "X-Tenant-Signature": signature,
    ...(req.headers.cookie ? { "Cookie": req.headers.cookie } : {}), // Forward cookie header
    ...(options.headers || {}), // Merge any additional headers from options
  };

  return fetch(targetUrl, {
    ...options,
    headers: headers,
  });
}