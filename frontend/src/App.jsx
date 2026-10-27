import { useState } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
} from "react-router-dom";

import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";

import Dashboard from "./pages/Dashboard";
import LiveMonitoring from "./pages/LiveMonitoring";
import EmergencyCenter from "./pages/EmergencyCenter";
import AIAnalysis from "./pages/AIAnalysis";
import IncidentHistory from "./pages/IncidentHistory";
import IoTDevices from "./pages/IoTDevices";
import QRAccess from "./pages/QRAccess";
import Settings from "./pages/Settings";

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const closeSidebar = () => {
    setSidebarOpen(false);
  };

  return (
    <BrowserRouter>
      <div className="app-layout">

        <Sidebar
          isOpen={sidebarOpen}
          onClose={closeSidebar}
        />

        {sidebarOpen && (
          <div
            className="sidebar-overlay"
            onClick={closeSidebar}
          />
        )}

        <div className="main-wrapper">

          <Navbar
            onMenuClick={() => setSidebarOpen(true)}
          />

          <main className="main-content">
            <Routes>

              <Route
                path="/"
                element={<Dashboard />}
              />

              <Route
                path="/live-monitoring"
                element={<LiveMonitoring />}
              />

              <Route
                path="/emergency"
                element={<EmergencyCenter />}
              />

              <Route
                path="/ai-analysis"
                element={<AIAnalysis />}
              />

              <Route
                path="/incidents"
                element={<IncidentHistory />}
              />

              <Route
                path="/iot"
                element={<IoTDevices />}
              />

              <Route
                path="/qr-access"
                element={<QRAccess />}
              />

              <Route
                path="/settings"
                element={<Settings />}
              />

            </Routes>
          </main>

        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;