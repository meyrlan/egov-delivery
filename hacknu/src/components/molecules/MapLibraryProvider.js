import { useState, createContext, useContext } from "react";
import Script from "next/script";

const MapLibraryLoadedContext = createContext(null);

export const MapLibraryProvider = ({ children }) => {
  const [isLoaded, setIsLoaded] = useState(false);

  return (
    <>
      <Script
        crossOrigin="anonymous"
        src="https://api-maps.yandex.ru/2.1/?apikey=64a40e41-9d55-41fb-9c6f-ae3092d0ecdd&lang=ru_RU"
        onReady={() => setIsLoaded(true)}
        onError={() => setIsLoaded(false)}
      />
      <MapLibraryLoadedContext.Provider value={isLoaded}>
        {children}
      </MapLibraryLoadedContext.Provider>
    </>
  );
};

export const useMapIsLoaded = () => {
  const value = useContext(MapLibraryLoadedContext);

  if (value === null) {
    throw new Error();
  }

  return value;
};
