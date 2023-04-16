import { Flex, Stack, Group, Button, Paper, Text } from "@mantine/core";
import { useQuery } from "@tanstack/react-query";

import { BaseApi } from "@/api";

export const AdminCouriers = () => {
  const { data, status } = useQuery(["courier-companies"], () =>
    BaseApi.get("/courier_company")
  );

  if ((status !== "success") | !data) return null;

  return (
    <Stack>
      <Group>
        <Button size="xs">Добавить компанию</Button>
      </Group>
      {data.data.map((company) => (
        <Paper
          key={company.id}
          withBorder
          shadow="sm"
          py={8}
          px={12}
          radius="sm"
        >
          <Flex justify="space-between" align="center">
            <Text>{company.name}</Text>
            <Button variant="outline" size="xs">
              Добавить курьера
            </Button>
          </Flex>
        </Paper>
      ))}
    </Stack>
  );
};
