import axios from "axios";

export const ClientApi = axios.create({
  baseURL: "http://127.0.0.1:8888/api",
});
