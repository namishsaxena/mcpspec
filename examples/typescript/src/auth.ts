import http from "node:http";
import crypto from "node:crypto";
import type { OAuthTokenVerifier } from "@modelcontextprotocol/sdk/server/auth/provider.js";
import type { AuthInfo } from "@modelcontextprotocol/sdk/server/auth/types.js";
import { InvalidTokenError } from "@modelcontextprotocol/sdk/server/auth/errors.js";

// ---------------------------------------------------------------------------
// Bearer token auth (protects /mcp only — docs and spec stay public)
// ---------------------------------------------------------------------------

export const API_TOKEN = process.env.API_TOKEN ?? "mcpspec-demo-token";

function timingSafeEqual(a: string, b: string): boolean {
  const hmacA = crypto.createHmac("sha256", API_TOKEN).update(a).digest();
  const hmacB = crypto.createHmac("sha256", API_TOKEN).update(b).digest();
  return crypto.timingSafeEqual(hmacA, hmacB);
}

export const tokenVerifier: OAuthTokenVerifier = {
  async verifyAccessToken(token: string): Promise<AuthInfo> {
    if (!timingSafeEqual(token, API_TOKEN)) {
      throw new InvalidTokenError("Invalid access token");
    }
    return {
      token,
      clientId: "demo-client",
      scopes: ["mcp:access"],
    };
  },
};

export function extractBearerToken(req: http.IncomingMessage): string | null {
  const header = req.headers.authorization;
  if (!header?.startsWith("Bearer ")) return null;
  return header.slice(7);
}
