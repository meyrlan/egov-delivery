import { Container, Tabs, Text } from "@mantine/core";

import {
  CourierProfile,
  CourierMyRequests,
  CourierAllRequests,
} from "../molecules";

export const CourierSystem = () => {
  return (
    <Container size={1600}>
      <Tabs defaultValue="profile">
        <Tabs.List position="center">
          <Tabs.Tab value="profile">
            <Text size="sm">Профиль</Text>
          </Tabs.Tab>
          <Tabs.Tab value="my-requests">Мои заказы</Tabs.Tab>
          <Tabs.Tab value="available-requests">Все заказы</Tabs.Tab>
        </Tabs.List>
        <Tabs.Panel value="profile" pt="xs">
          <CourierProfile />
        </Tabs.Panel>
        <Tabs.Panel value="my-requests" pt="xs">
          <CourierMyRequests />
        </Tabs.Panel>
        <Tabs.Panel value="available-requests" pt="xs">
          <CourierAllRequests />
        </Tabs.Panel>
      </Tabs>
    </Container>
  );
};
