import { useState, useEffect } from "react";

import { auth } from "./auth";

export const AuthRoute = ({ children }) => {
  const [isSignedIn, setIsSignedIn] = useState(null);

  useEffect(() => {
    return auth.subscribe(() => {
      setIsSignedIn(auth.isSignedIn());
    });
  }, []);

  if (isSignedIn === null) return null;

  return <>{children(auth.isSignedIn())}</>;
};
