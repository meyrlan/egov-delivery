import { Container, Paper, Stack, Title, Text } from "@mantine/core";
import { useRouter } from "next/router";

import { useQuery } from "@tanstack/react-query";
import { ClientApi } from "@/api";

const ORDER_STATUS = [
  "Ready",
  "Оплачен",
  "Назначен курьер",
  "Курьер в пути",
  "Документ передан",
];

const OrderedRequest = () => {
  const router = useRouter();

  const { request_id } = router.query;

  const { data, status } = useQuery(["ordered-request", request_id], () =>
    ClientApi.get(`/document_order/get_info/${request_id}`)
  );

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
        </Stack>
      </Paper>
    </Container>
  );
};

export async function getStaticProps() {
  return {
    props: {
      ignoreAuth: true,
    },
  };
}

export default OrderedRequest;
