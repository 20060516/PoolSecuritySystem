import {
  Menu,
  Activity,
} from "lucide-react";

function Navbar({ onMenuClick }) {
  return (
    <header className="navbar">

      <div className="navbar-left">

        <button
          className="menu-button"
          onClick={onMenuClick}
          aria-label="Open menu"
        >
          <Menu size={20} />
        </button>

        <div>
          <h1 className="navbar-title">
            AquaGuard
          </h1>

          <p className="navbar-subtitle">
            AI Pool Safety Monitoring
          </p>
        </div>

      </div>

      <div className="navbar-right">

        <div className="system-status">

          <span className="status-dot"></span>

          <Activity size={15} />

          <span>
            System Online
          </span>

        </div>

      </div>

    </header>
  );
}

export default Navbar;