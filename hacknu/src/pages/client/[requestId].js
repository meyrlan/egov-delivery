import {
  Container,
  Stack,
  Title,
  Text,
  TextInput,
  Button,
  Paper,
  Group,
  Checkbox,
  Modal,
  Center,
  LoadingOverlay,
  Anchor,
} from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { useForm } from "@mantine/form";
import { useRouter } from "next/router";
import { useMutation } from "@tanstack/react-query";
import { DateTimePicker } from "@mantine/dates";
import toast from "react-hot-toast";
import { useState, useRef } from "react";
import { addDays } from "date-fns";

import { CourierDeliverySelect } from "@/components/atoms";
import { IINInput } from "@/components/molecules";
import { PlacePicker } from "@/components/organisms";
import { ClientApi } from "@/api";

const ORDER_STATUS = [
  "Ready",
  "Paid",
  "Courier assigned",
  "Courier on the way",
  "Handed",
];

export default function RequestForm() {
  const [authedUser, setAuthedUser] = useState(null);

  return (
    <>
      <Container size={700} my={10} p={4}>
        <Paper p={16}>
          {!authedUser ? (
            <AuthForm onAuth={setAuthedUser} />
          ) : (
            <DeliveryForm {...authedUser} />
          )}
        </Paper>
      </Container>
    </>
  );
}

/*
 *    <DeliveryForm
        client={{
          iin: "011209500519",
          name: "Нуртау",
          surname: "Тоганбай",
          phoneNumber: "87713222777",
          address:
            "КАЗАХСТАН АСТАНА САРЫАРКА РАЙОН УЛИЦА Ақбұғы дом 5/1 квартира 45",
        }}
      />

 */

const AuthForm = ({ onAuth }) => {
  const router = useRouter();
  const requestId = router.query.requestId;

  const form = useForm({
    initialValues: {
      iin: "",
    },

    validate: {
      iin: (value) =>
        value.length !== 12 || Number.isNaN(Number(value))
          ? "ИИН должен содержать 12 цифр"
          : null,
    },
  });

  const mutation = useMutation({
    mutationFn: (body) => ClientApi.post("/document_order", body),
    onSuccess: ({ data }) => {
      const status = ORDER_STATUS[data.status];

      if (status !== "Ready") {
        router.replace(
          `/ordered?request_id=${data.request_id}&iin=${data.client.iin}`
        );
      }

      onAuth(data);
    },
    onError: () => {
      toast.error("Ошибка, пожалуйста проверьте валидность ссылки и ИИН");
    },
  });

  return (
    <Stack spacing="xs">
      <div>
        <Title order={4}>Номер документа: {requestId}</Title>
        <Text color="dimmed" size="sm">
          Пожалуйста заполните ИИН чтобы перейти к заказу доставки
        </Text>
      </div>
      <form
        onSubmit={form.onSubmit((values) =>
          mutation.mutate({
            iin: values.iin,
            request_id: requestId,
          })
        )}
      >
        <Stack spacing="sm">
          <TextInput label="ИИН" required {...form.getInputProps("iin")} />
          <Button fullWidth type="submit">
            Перейти к разделу доставки
          </Button>
        </Stack>
      </form>
    </Stack>
  );
};

const DeliveryForm = ({ client }) => {
  const router = useRouter();
  const requestId = router.query.requestId;

  const [step, setStep] = useState("first");

  const form = useForm({
    validate: {},
  });

  const mutation = useMutation({
    mutationFn: (body) => ClientApi.patch(`/document_order/${requestId}`, body),
    onSuccess: ({ data }) => {
      window.location.href = data.url;
    },
    onError: () => {
      toast.error("Ошибка, пожалуйста проверьте соединение");
    },
  });

  if (step === "first") {
    return (
      <DeliveryFirstForm
        client={client}
        initialValues={form.values}
        onSubmit={(values) => {
          form.setValues((prevValues) => ({ ...prevValues, ...values }));
          setStep("second");
        }}
      />
    );
  }

  if (step === "second") {
    return (
      <DeliverySecondForm
        client={client}
        initialValues={form.values}
        onSubmit={(values) => {
          form.setValues((prevValues) => ({ ...prevValues, ...values }));
          setStep("third");
        }}
        back={() => {
          setStep("first");
        }}
      />
    );
  }

  return (
    <DeliveryFinalForm
      client={client}
      initialValues={form.values}
      back={() => {
        setStep("second");
      }}
      onSubmit={(values) => {
        mutation.mutate(values);
      }}
    />
  );
};

const DeliveryFinalForm = ({ client, initialValues, back, onSubmit }) => {
  const form = useForm({
    initialValues: {
      ...initialValues,
      firstCheckbox: false,
      secondCheckbox: false,
      is_cashback_used: false,
    },
    validate: {
      courier_company_id: (value) =>
        value === undefined ? "Обязательное поле" : null,
      delivery_datetime: (value) =>
        value === undefined ? "Обязательное поле" : null,
    },
  });

  return (
    <Stack>
      <form onSubmit={form.onSubmit(onSubmit)}>
        <DateTimePicker
          label="Выберите время доставки"
          {...form.getInputProps("delivery_datetime")}
          mx="auto"
          minDate={addDays(new Date(), 1)}
        />
        <div>
          <Checkbox
            mt={8}
            label={`У вас имеется ${client.cashback} кэшбека. Отметьте поле если хотите потратить кэшбек`}
            {...form.getInputProps("is_cashback_used")}
          />
          <CourierDeliverySelect
            form={form}
            cashback={form.values.is_cashback_used ? client.cashback : null}
          />
        </div>
        <Checkbox
          mt={8}
          label={
            <>
              Я принимаю условия{" "}
              <Anchor href="/documents/public" target="_blank">
                публичного договора-оферты
              </Anchor>
            </>
          }
          {...form.getInputProps("firstCheckbox")}
        />
        <Checkbox
          label={
            <>
              Я ознакомлен и согласен с{" "}
              <Anchor href="/documents/public" target="_blank">
                условиями политики конфиденциальности и персональных данных
              </Anchor>
            </>
          }
          {...form.getInputProps("secondCheckbox")}
        />
        <Center mt={16}>
          <Group>
            <Button variant="outline" onClick={back}>
              Назад
            </Button>
            <Button type="submit" disabled={!form.isValid()}>
              Оплатить
            </Button>
          </Group>
        </Center>
      </form>
    </Stack>
  );
};

const DeliveryFirstForm = ({ client, initialValues, onSubmit }) => {
  const form = useForm({
    initialValues: {
      phone_number: client.phone_number,
      trusted_user_iin: "",
      ...initialValues,
    },
  });

  console.log(form.values);
  const [isAnotherReceiver, setIsAnotherReceiver] = useState(
    form.values.trusted_user_iin !== ""
  );

  return (
    <Stack spacing="xl">
      <Paper withBorder shadow="xs" radius="md" p={8}>
        <div>
          <Title order={4} mb={4}>
            Владелец документа
          </Title>
          <div>
            <Text size="sm">ИИН: {client.iin}</Text>
            <Text size="sm">Фамилия: {client.lastname}</Text>
            <Text size="sm">Имя: {client.firstname}</Text>
            <Text size="sm">Отчество: {client.middlename}</Text>
          </div>
        </div>
      </Paper>
      <form onSubmit={form.onSubmit(onSubmit)}>
        <Title order={6} mb={8}>
          Заполните следующие поля чтобы заказать доставку
        </Title>
        <Stack spacing="xs">
          <Stack>
            <TextInput
              label="Номер телефона"
              required
              {...form.getInputProps("phone_number")}
            />
            <Paper withBorder p={8} shadow="xs" radius="md">
              <Checkbox
                label="Я не смогу принять доставку и хочу указать другого человека"
                onChange={(event) => {
                  setIsAnotherReceiver(event.target.checked);
                }}
                defaultValue={isAnotherReceiver}
                value={isAnotherReceiver}
                checked={isAnotherReceiver}
              />
              {isAnotherReceiver && (
                <IINInput
                  initialValue={form.values.trusted_user_iin}
                  onSubmit={(iin) => {
                    form.setValues((prevValues) => ({
                      ...prevValues,
                      trusted_user_iin: iin,
                    }));
                  }}
                />
              )}
            </Paper>
          </Stack>
          <Button fullWidth type="submit">
            Дальше
          </Button>
        </Stack>
      </form>
    </Stack>
  );
};

const DeliverySecondForm = ({ client, initialValues, back, onSubmit }) => {
  const form = useForm({
    initialValues: {
      delivery_address: {
        region: "",
        city: "",
        street: "",
        house_number: "",
        apartment: "",
        entrance: "",
        floor: "",
        block: "",
        apartment_complex: "",
        additional_information: "",
        ...initialValues,
      },
    },
    validate: {},
  });

  const lastSubmittedValues = useRef(form.values);

  const [opened, { open, close }] = useDisclosure(false);

  const router = useRouter();
  const requestId = router.query.requestId;

  const mutation = useMutation({
    mutationFn: (body) => ClientApi.patch(`/document_order/${requestId}`, body),
    onSuccess: () => {
      onSubmit(lastSubmittedValues.current);
    },
  });

  return (
    <>
      <form
        onSubmit={form.onSubmit((values) => {
          lastSubmittedValues.current = { ...values };
          mutation.mutate(values);
        })}
        style={{ position: "relative" }}
      >
        <LoadingOverlay visible={mutation.isLoading} overlayBlur={2} />
        <Stack spacing="xs">
          <Stack spacing={8}>
            <div>
              <Text size="sm" weight={500}>
                Адрес доставки
              </Text>
              <Text color="dimmed" size="sm">
                Если хотите указать на карте и автоматически заполнить некоторые
                поля, то нажмите{" "}
                <Button variant="outline" size="xs" p={3} onClick={open}>
                  сюда
                </Button>
              </Text>
            </div>
            <Stack spacing={4}>
              <TextInput
                label="Область"
                required
                {...form.getInputProps("delivery_address.region")}
              />
              <TextInput
                label="Город"
                required
                {...form.getInputProps("delivery_address.city")}
              />
              <TextInput
                label="Улица"
                required
                {...form.getInputProps("delivery_address.street")}
              />
              <TextInput
                label="Номер дома"
                required
                {...form.getInputProps("delivery_address.house_number")}
              />
              <TextInput
                label="Квартира"
                {...form.getInputProps("delivery_address.apartment")}
              />
              <TextInput
                label="Подъезд"
                {...form.getInputProps("delivery_address.entrance")}
              />
              <TextInput
                label="Этаж"
                {...form.getInputProps("delivery_address.floor")}
              />
              <TextInput
                label="Корпус"
                {...form.getInputProps("delivery_address.block")}
              />
              <TextInput
                label="Наименование ЖК"
                {...form.getInputProps("delivery_address.apartment_complex")}
              />
              <TextInput
                label="Дополнительная информация"
                {...form.getInputProps(
                  "delivery_address.additional_information"
                )}
              />
            </Stack>
          </Stack>
          <Center>
            <Group>
              <Button variant="outline" onClick={back}>
                Назад
              </Button>
              <Button type="submit">Дальше</Button>
            </Group>
          </Center>
        </Stack>
      </form>
      <Modal
        opened={opened}
        onClose={close}
        padding={0}
        fullScreen
        styles={{
          content: {
            display: "flex",
            flexDirection: "column",
          },
          header: {
            display: "none",
          },
          body: {
            width: "auto",
            flex: 1,
          },
        }}
      >
        <PlacePicker
          fetchedAddress={client.home_address}
          onClose={close}
          onChange={(values) => {
            form.setValues((prevValues) => ({
              ...prevValues,
              delivery_address: {
                region: "",
                city: "",
                street: "",
                house_number: "",
                apartment: "",
                entrance: "",
                floor: "",
                block: "",
                apartment_complex: "",
                ...values,
              },
            }));
          }}
        />
      </Modal>
    </>
  );
};

export const getStaticPaths = async () => {
  return {
    paths: [], //indicates that no page needs be created at build time
    fallback: "blocking", //indicates the type of fallback
  };
};

export async function getStaticProps() {
  return {
    props: {
      ignoreAuth: true,
    },
  };
}
