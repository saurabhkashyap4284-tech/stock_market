import Header from "../components/layout/Header";
import DashboardWidgets from "../components/dashboard/DashboardWidgets";
import StockTable from "../components/table/StockTable";
import AlertToasts from "../components/layout/AlertToasts";
import { useWebSocket } from "../hooks/useWebSocket";

export default function DashboardPage() {
  useWebSocket();

  return (
    <div style={{ minHeight: "100vh", backgroundColor: "#0f172a" }}>
      <Header />
      <DashboardWidgets />
      <StockTable />
      <AlertToasts />
    </div>
  );
}
