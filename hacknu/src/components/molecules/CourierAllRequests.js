import { useQuery, useQueryClient, useMutation } from "@tanstack/react-query";
import { Stack, Flex, Paper, Button, Text } from "@mantine/core";
import toast from "react-hot-toast";

import { BaseApi } from "@/api";

import { useMe } from "./MeProvider";

export const CourierAllRequests = () => {
  const queryClient = useQueryClient();
  const me = useMe();

  const { data, status } = useQuery(["all-requests"], () =>
    BaseApi.get(`/document_orders/${me.courier_company}`)
  );

  const mutation = useMutation({
    mutationFn: (body) => BaseApi.post("/document_order/pick", body),
    onSuccess: () => {
      toast.success("Успешно взят");
      queryClient.invalidateQueries({
        queryKey: [["all-requests"], ["my-requests"]],
      });
    },
    onError: () => {
      toast.error("Ошибка, пожалуйста проверьте соединение");
    },
  });

  if (status !== "success" || !data) return null;

  return (
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
              onClick={() => {
                mutation.mutate({
                  request_id: request.request_id,
                });
              }}
            >
              Взять
            </Button>
          </Flex>
        </Paper>
      ))}
    </Stack>
  );
};
