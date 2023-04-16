import { Select } from "@mantine/core";
import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";
import { useRouter } from "next/router";

import { ClientApi } from "@/api";

export const CourierDeliverySelect = ({ form, cashback }) => {
  const router = useRouter();
  const requestId = router.query.requestId;

  const { data, status } = useQuery(["courier-deliveries"], () =>
    ClientApi.get(`/courier_companies?request_id=${requestId}`)
  );

  const companies = data?.data;

  const preparedData = useMemo(() => {
    if (!companies) return [];

    return companies.companies.map((company) => ({
      value: company.id,
      label:
        cashback === null
          ? `${company.name} ${company.price}тг`
          : `${company.name} ${company.price} - ${cashback}тг`,
    }));
  }, [companies, cashback]);

  return (
    <Select
      data={preparedData}
      label="Служба доставки"
      disabled={status !== "success"}
      {...form?.getInputProps("courier_company_id")}
    />
  );
};
