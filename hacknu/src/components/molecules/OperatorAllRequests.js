import {
  Stack,
  Flex,
  Group,
  Title,
  Paper,
  Button,
  Text,
  Modal,
} from "@mantine/core";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { OperatorOrder } from "./OperatorOrder";

import { BaseApi } from "@/api";

const ORDER_STATUS = [
  "Ready",
  "Оплачен",
  "Назначен курьер",
  "Курьер в пути",
  "Документ передан",
];

export const OperatorAllRequests = () => {
  const [requestId, setRequestId] = useState(null);
  const { data, status } = useQuery(["my-requests"], () =>
    BaseApi.get("/document_orders")
  );

  if (status !== "success" || !data) return null;

  console.log(data, status);

  return (
    <>
      <Title order={3}>Заявки</Title>
      <Stack>
        {data.data.map((request) => (
          <Paper
            key={request.request_id}
            withBorder
            shadow="sm"
            py={8}
            px={12}
            radius="sm"
          >
            <Flex justify="space-between" align="center">
              <Group>
                <Text>{request.request_id}</Text>
                <Text>{ORDER_STATUS[request.status]}</Text>
              </Group>
              <Button
                variant="outline"
                size="xs"
                onClick={() => setRequestId(request.request_id)}
              >
                Посмотреть
              </Button>
            </Flex>
          </Paper>
        ))}
      </Stack>
      <Modal
        opened={requestId !== null}
        onClose={() => setRequestId(null)}
        padding={0}
        fullScreen
      >
        {requestId && <OperatorOrder request_id={requestId} />}
      </Modal>
    </>
  );
};
