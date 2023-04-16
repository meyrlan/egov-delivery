import { useState, useEffect, useRef } from "react";

import { useMapIsLoaded } from "./MapLibraryProvider";

export const useMap = (mapId) => {
  const [map, setMap] = useState(null);
  const mapRef = useRef(null);
  const isMapLoaded = useMapIsLoaded();

  useEffect(() => {
    if (!isMapLoaded) return;

    const init = () => {
      if (mapRef.current) {
        mapRef.current.destroy();
      }

      mapRef.current = new ymaps.Map(mapId, {
        center: [0, 0],
        zoom: 15,
        controls: ["zoomControl"],
      });

      const searchControl = new ymaps.control.SearchControl({
        options: {
          noPlacemark: true,
        },
      });

      mapRef.current.controls.add(searchControl);

      setMap(mapRef.current);
    };

    ymaps.ready(init);

    return () => {
      if (mapRef.current) {
        mapRef.current.destroy();
      }
    };
  }, [isMapLoaded]);

  return map;
};
