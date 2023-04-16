import {
  TextInput,
  Stack,
  Text,
  Button,
  LoadingOverlay,
  Title,
  Paper,
} from "@mantine/core";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "@mantine/form";
import { useState } from "react";
import toast from "react-hot-toast";

import { ClientApi } from "@/api";

export const IINInput = ({ onSubmit, initialValue }) => {
  const [receiver, setReceiver] = useState(null);
  const form = useForm({
    initialValues: {
      iin: initialValue ?? "",
    },

    validate: {
      iin: (value) =>
        value.length !== 12 || Number.isNaN(Number(value))
          ? "ИИН должен содержать 12 цифр"
          : null,
    },
  });

  const mutation = useMutation({
    mutationFn: (body) => ClientApi.post("/user_by_iin", body),
    onSuccess: ({ data }) => {
      setReceiver(data);
    },
    onError: () => {
      toast.error("Ошибка, пожалуйста проверьте валидность ИИН получателя");
    },
  });

  return (
    <div style={{ position: "relative" }}>
      <LoadingOverlay visible={mutation.isLoading} overlayBlur={2} />
      <div>
        <TextInput
          label="ИИН получателя"
          required
          {...form.getInputProps("iin")}
        />
        <Button
          mt={8}
          variant="outline"
          onClick={() => {
            form.setTouched({ iin: true });
            form.validate();
            const isValid = form.isValid("iin");

            if (!isValid) return;

            onSubmit(form.values.iin);
            mutation.mutate(form.values);
          }}
        >
          Загрузить данные с базы
        </Button>
      </div>
      {receiver && mutation.isSuccess && (
        <Paper withBorder radius="md" mt={12} p={8}>
          <div>
            <Title order={4} mb={4}>
              Получатель
            </Title>
            <div>
              <Text size="sm">ИИН: {receiver.iin}</Text>
              <Text size="sm">Фамилия: {receiver.lastName}</Text>
              <Text size="sm">Имя: {receiver.firstName}</Text>
              <Text size="sm">Отчество: {receiver.middleName}</Text>
              {receiver.phone && (
                <Text size="sm">Номер телефона: {receiver.phone}</Text>
              )}
            </div>
          </div>
        </Paper>
      )}
    </div>
  );
};
