import { useMe } from "@/components/molecules";
import {
  OperatorSystem,
  CourierSystem,
  AdminSystem,
} from "@/components/organisms";

const SystemPage = () => {
  const me = useMe();

  if (me.role === "courier") {
    return <CourierSystem />;
  }

  if (me.role === "operator") {
    return <OperatorSystem />;
  }

  return <AdminSystem />;
};

export default SystemPage;
