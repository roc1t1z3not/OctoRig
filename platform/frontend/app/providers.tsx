"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { WSProvider } from "@/providers/WSProvider";
import { useUserStore } from "@/stores/user.store";
import { refreshToken } from "@/lib/api/auth";

export function Providers({ children }: { children: React.ReactNode }) {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: { queries: { staleTime: 10_000, retry: 1 } },
      })
  );

  // Silent token restore: user metadata is persisted in localStorage but the access token
  // lives only in memory. On every page load, if we have user data but no token, hit
  // /auth/refresh — the browser sends the HttpOnly cookie automatically.
  useEffect(() => {
    const { user, accessToken, setAccessToken, clearSession, setIsRestoringToken } =
      useUserStore.getState();
    if (user && !accessToken) {
      refreshToken()
        .then(({ access_token }) => setAccessToken(access_token))
        .catch(() => clearSession())
        .finally(() => setIsRestoringToken(false));
    }
  }, []);

  return (
    <QueryClientProvider client={client}>
      <WSProvider>{children}</WSProvider>
    </QueryClientProvider>
  );
}
