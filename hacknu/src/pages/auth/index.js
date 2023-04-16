import {
  TextInput,
  PasswordInput,
  Paper,
  Title,
  Container,
  Button,
  Stack,
} from "@mantine/core";
import { useForm } from "@mantine/form";
import toast from "react-hot-toast";
import { useMutation } from "@tanstack/react-query";

import { BaseApi } from "@/api";
import { auth } from "@/auth";

export default function LoginPage() {
  const form = useForm({
    initialValues: {
      iin: "",
      password: "",
    },

    validate: {
      iin: (value) =>
        value.length !== 12 || Number.isNaN(Number(value))
          ? "ИИН должен содержать 12 цифр"
          : null,
    },
  });

  const mutation = useMutation({
    mutationFn: (body) => BaseApi.post("/token", body),
    onSuccess: ({ data }) => {
      auth.updateToken(data.access);
      toast.success("Успех!");
    },
    onError: () => {
      toast.error("Ошибка, пожалуйста проверьте валидность данных");
    },
  });

  return (
    <Container size={700} my={40}>
      <Title
        align="center"
        sx={(theme) => ({
          fontFamily: `Greycliff CF, ${theme.fontFamily}`,
          fontWeight: 900,
        })}
      >
        Войти в систему!
      </Title>
      <Paper withBorder shadow="md" p={16} mt={30} radius="md">
        <form
          onSubmit={form.onSubmit((values) => {
            mutation.mutate(values);
          })}
        >
          <Stack>
            <TextInput label="ИИН" required {...form.getInputProps("iin")} />
            <PasswordInput
              label="Пароль"
              required
              {...form.getInputProps("password")}
            />
          </Stack>
          <Button fullWidth mt="xl" type="submit">
            Войти
          </Button>
        </form>
      </Paper>
    </Container>
  );
}

export async function getStaticProps() {
  return {
    props: {
      shouldBeSignedIn: false,
    },
  };
}
