import {
  LayoutDashboard,
  Video,
  AlertTriangle,
  Brain,
  History,
  Cpu,
  QrCode,
  Settings,
  X,
} from "lucide-react";

import { NavLink } from "react-router-dom";

function Sidebar({ isOpen, onClose }) {

  const menuItems = [
    {
      name: "Dashboard",
      path: "/",
      icon: LayoutDashboard,
    },
    {
      name: "Live Monitoring",
      path: "/live-monitoring",
      icon: Video,
    },
    {
      name: "Emergency Center",
      path: "/emergency",
      icon: AlertTriangle,
    },
    {
      name: "AI Analysis",
      path: "/ai-analysis",
      icon: Brain,
    },
    {
      name: "Incident History",
      path: "/incidents",
      icon: History,
    },
    {
      name: "IoT Devices",
      path: "/iot",
      icon: Cpu,
    },
    {
      name: "Settings",
      path: "/settings",
      icon: Settings,
    },
  ];

  return (
    <aside
      className={`sidebar ${
        isOpen ? "sidebar-open" : ""
      }`}
    >

      <div className="sidebar-header">

        <div className="brand-mark">
          AG
        </div>

        <div className="brand-info">
          <h2>AquaGuard</h2>
          <span>Pool Safety AI</span>
        </div>

        <button
          className="sidebar-close"
          onClick={onClose}
          aria-label="Close menu"
        >
          <X size={20} />
        </button>

      </div>

      <div className="sidebar-section-title">
        Navigation
      </div>

      <nav className="sidebar-nav">

        {menuItems.map((item) => {

          const Icon = item.icon;

          return (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={onClose}
              className={({ isActive }) =>
                `sidebar-link ${
                  isActive ? "active" : ""
                }`
              }
            >
              <Icon size={17} />

              <span>
                {item.name}
              </span>
            </NavLink>
          );

        })}

      </nav>

      <div className="sidebar-footer">

        <div className="connection-indicator">

          <span className="connection-dot"></span>

          <div>
            <strong>
              Backend Connected
            </strong>

            <small>
              System ready
            </small>
          </div>

        </div>

        <div className="sidebar-version">
          AquaGuard v1.0
        </div>

      </div>

    </aside>
  );
}

export default Sidebar;