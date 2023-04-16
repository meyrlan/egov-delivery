import { Container, Tabs, Text } from "@mantine/core";

import { AdminCouriers } from "../molecules";

export const AdminSystem = () => {
  return (
    <Container size={1600}>
      <Tabs defaultValue="couriers">
        <Tabs.List position="center">
          <Tabs.Tab value="couriers">
            <Text size="sm">Профиль</Text>
          </Tabs.Tab>
          <Tabs.Tab value="operators">Операторы</Tabs.Tab>
        </Tabs.List>
        <Tabs.Panel value="couriers" pt="xs">
          <AdminCouriers />
        </Tabs.Panel>
        <Tabs.Panel value="operators" pt="xs">
          Операторы
        </Tabs.Panel>
      </Tabs>
    </Container>
  );
};
