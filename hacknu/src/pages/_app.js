import Head from "next/head";
import { MantineProvider } from "@mantine/core";
import { Toaster } from "react-hot-toast";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { AuthRoute } from "@/auth";
import { Switch } from "@/navigation";
import { MapLibraryProvider, MeProvider } from "@/components/molecules";

const queryClient = new QueryClient();

export default function App(props) {
  const { Component, pageProps } = props;

  return (
    <>
      <Head>
        <title>Page title</title>
        <meta
          name="viewport"
          content="minimum-scale=1, initial-scale=1, width=device-width"
        />
      </Head>
      <MapLibraryProvider>
        <MantineProvider
          withGlobalStyles
          withNormalizeCSS
          theme={{
            colorScheme: "light",
          }}
        >
          <QueryClientProvider client={queryClient}>
            {pageProps.ignoreAuth ? (
              <Component {...pageProps} />
            ) : (
              <AuthRoute>
                {(isSignedIn) => (
                  <Switch
                    isSignedIn={isSignedIn}
                    shouldBeSignedIn={pageProps.shouldBeSignedIn}
                  >
                    {isSignedIn ? (
                      <MeProvider>
                        <Component {...pageProps} />
                      </MeProvider>
                    ) : (
                      <Component {...pageProps} />
                    )}
                  </Switch>
                )}
              </AuthRoute>
            )}
          </QueryClientProvider>
        </MantineProvider>
      </MapLibraryProvider>
      <Toaster
        toastOptions={{
          duration: 3000,
        }}
      />
    </>
  );
}
