import { Title, Stack, Text } from "@mantine/core";
import { useMe } from "./MeProvider";

export const CourierProfile = () => {
  const me = useMe();

  return (
    <Stack spacing="sm">
      <Title order={3}>Мои данные</Title>
      <div>
        <Text>ИИН: {me.iin}</Text>
        <Text>Номер телефона: {me.phone_number}</Text>
        <Text>Компания доставки: {me.courier_company}</Text>
      </div>
    </Stack>
  );
};
