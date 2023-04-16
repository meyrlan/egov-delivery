import { useId, useLayoutEffect, useState } from "react";
import {
  Flex,
  Group,
  Button,
  Center,
  Box,
  Text,
  LoadingOverlay,
} from "@mantine/core";

import { ClientApi } from "@/api";
import { useMutation } from "@tanstack/react-query";

import { useMap } from "../molecules";

const mapper = {
  province: "region",
  locality: "city",
  street: "street",
  house: "house_number",
};

const transformPlaceLocation = (raw) => {
  const data = {};
  const components = raw.Address.Components;

  components.forEach((component) => {
    if (
      component.kind === "district" &&
      component.name.includes("жилой комплекс")
    ) {
      data["apartment_complex"] = component.name;
    } else {
      const correspondence = mapper[component.kind];
      if (correspondence) {
        data[correspondence] = component.name;
      }
    }
  });

  return {
    formatted: raw.Address.formatted,
    ...data,
  };
};

export const PlacePicker = ({ fetchedAddress, onClose, onChange }) => {
  const mapId = useId();
  const map = useMap(mapId);

  const [isMapFullyInitialized, setIsMapFullyInitialized] = useState(false);
  const [placeSelected, setPlaceSelected] = useState(null);

  useLayoutEffect(() => {
    if (!map) return;

    ymaps
      .geocode(fetchedAddress)
      .then((res) => {
        const coords = res.geoObjects.get(0).properties._data.boundedBy[0];
        map.setCenter(coords);
        setIsMapFullyInitialized(true);
      })
      .catch(() => {
        setIsMapFullyInitialized(true);
      });
  }, [map, fetchedAddress]);

  useLayoutEffect(() => {
    if (!map) return;

    map.events.add("click", function (e) {
      const coords = e.get("coords");

      map.geoObjects.removeAll();

      const pointMarker = new ymaps.GeoObject({
        geometry: {
          type: "Point",
          coordinates: coords,
        },
      });

      ymaps.geocode(coords).then((res) => {
        const properties = res.geoObjects.get(0).properties;
        const data = transformPlaceLocation(
          properties.get("metaDataProperty").GeocoderMetaData
        );
        setPlaceSelected(data);
      });

      map.geoObjects.add(pointMarker);
    });
  }, [map]);

  return (
    <Flex
      direction="column"
      sx={{
        height: "100%",
      }}
    >
      <div id={mapId} style={{ flex: 1, position: "relative" }}>
        <LoadingOverlay visible={!isMapFullyInitialized} overlayBlur={5} />
      </div>
      <Box sx={{ padding: 8 }}>
        {placeSelected === null ? (
          <Text size="sm">Нажмите на карту чтобы выбрать место</Text>
        ) : (
          <Text size="sm">Выбранное место: {placeSelected?.formatted}</Text>
        )}
        <Center>
          <Group p="md">
            <Button
              disabled={placeSelected === null}
              onClick={() => {
                onChange(placeSelected);
                onClose();
              }}
            >
              Выбрать
            </Button>
            <Button variant="outline" onClick={onClose}>
              Отмена
            </Button>
          </Group>
        </Center>
      </Box>
    </Flex>
  );
};
