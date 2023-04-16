import { Center, Loader } from "@mantine/core";
import { createContext, useContext } from "react";
import { useQuery } from "@tanstack/react-query";

import { BaseApi } from "@/api";

const ROLES = ["admin", "courier", "operator"];

const MeContext = createContext(null);

export const MeProvider = ({ children }) => {
  const { data, status } = useQuery(["me"], () => BaseApi.get("/profile"));

  const profile = data?.data;
  if (status === "idle" || status === "loading") {
    return (
      <Center h="100vh" w="100vw">
        <Loader />
      </Center>
    );
  }

  if (status === "error" || !data) {
    return null;
  }

  return (
    <MeContext.Provider value={{ ...profile, role: ROLES[profile.role] }}>
      {children}
    </MeContext.Provider>
  );
};

export const useMe = () => {
  const me = useContext(MeContext);

  if (!me) {
    throw new Error("useMe must be used inside of MeProvider");
  }

  return me;
};
