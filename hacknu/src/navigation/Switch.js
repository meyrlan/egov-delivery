import { useRouter } from "next/router";
import { useMemo, useEffect } from "react";

export const Switch = ({ isSignedIn, shouldBeSignedIn = true, children }) => {
  const router = useRouter();

  const shouldRedirectTo = useMemo(() => {
    if (isSignedIn !== shouldBeSignedIn) {
      if (shouldBeSignedIn) {
        return "/auth";
      } else {
        return "/system";
      }
    } else {
      return null;
    }
  }, [isSignedIn, shouldBeSignedIn]);

  useEffect(() => {
    if (shouldRedirectTo) {
      router.replace(shouldRedirectTo);
    }
  }, [shouldRedirectTo]);

  if (shouldRedirectTo) return null;

  return <>{children}</>;
};
