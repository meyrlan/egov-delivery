import { Stack, Flex, Paper, Button, Text, Modal } from "@mantine/core";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { BaseApi } from "@/api";

import { CourierOrder } from "../molecules";

export const CourierMyRequests = () => {
  const [requestId, setRequestId] = useState(null);

  const { data, status } = useQuery(["my-requests"], () =>
    BaseApi.get("/document_orders/my")
  );

  if (status !== "success" || !data) return null;

  return (
    <>
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
              <Text>{request.request_id}</Text>
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
        {requestId && <CourierOrder request_id={requestId} />}
      </Modal>
    </>
  );
};
