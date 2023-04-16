import axios from "axios";

import { auth } from "@/auth";

export const BaseApi = axios.create({
  baseURL: "http://127.0.0.1:8888/api",
});

BaseApi.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response.status === 401) {
      auth.updateToken(null);
    }
    throw error;
  }
);

auth.subscribe((token) => {
  BaseApi.defaults.headers.common["Authorization"] = `Bearer ${token}`;
});
