import {
  Stack,
  Center,
  Paper,
  Button,
  Text,
  TextInput,
  Title,
  Modal,
  Container,
} from "@mantine/core";
import { useQuery, useQueryClient, useMutation } from "@tanstack/react-query";
import { useForm } from "@mantine/form";
import toast from "react-hot-toast";

import { BaseApi } from "@/api";
import { useDisclosure } from "@mantine/hooks";

const ORDER_STATUS = [
  "Ready",
  "Оплачен",
  "Назначен курьер",
  "Курьер в пути",
  "Документ передан",
];

export const OperatorOrder = ({ request_id }) => {
  const queryClient = useQueryClient();
  const [opened, { open, close }] = useDisclosure(false);

  const { data, status } = useQuery(["ordered-request", request_id], () =>
    BaseApi.get(`/document_order/get_info/${request_id}`)
  );

  const form = useForm({
    initialValues: {
      courier_code: "",
    },
  });

  const giveMutation = useMutation({
    mutationFn: (body) => BaseApi.post("/document_order/approve", body),
    onSuccess: () => {
      toast.success("Успешно передан документ");
      queryClient.invalidateQueries({
        queryKey: [["all-requests"], ["my-requests"]],
      });
      close();
    },
    onError: () => {
      toast.error("Ошибка, проверьте код");
    },
  });

  if (status !== "success" || !data) return null;

  return (
    <Container size={700} my={10} p={4}>
      <Paper p={16}>
        <Stack>
          <Title order={3}>
            Данные доставки документа: {data.data.request_id}
          </Title>
          <Text size="sm">Название документа: {data.data.service_name}</Text>
          <Text size="sm">Адрес доставки: {data.data.delivery_address}</Text>
          <Text size="sm">Время доставки: {data.data.delivery_datetime}</Text>
          <Text size="sm">
            Статус доставки: {ORDER_STATUS[data.data.status]}
          </Text>
          <Center>
            <Button onClick={open}>Передать курьеру</Button>
          </Center>
        </Stack>
      </Paper>
      <Modal opened={opened} onClose={close} fullScreen>
        <form
          onSubmit={form.onSubmit((values) => {
            giveMutation.mutate({
              request_id: data.data.request_id,
              courier_code: Number(values.courier_code),
            });
          })}
        >
          <TextInput
            label="Пароль"
            required
            {...form.getInputProps("courier_code")}
          />
          <Button fullWidth type="submit" mt={16}>
            Отправить
          </Button>
        </form>
      </Modal>
    </Container>
  );
};
