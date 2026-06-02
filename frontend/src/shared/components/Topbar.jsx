import { useEffect, useRef, useState } from "react";

function CalendarIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="3" y="4" width="18" height="18" rx="2" />
      <line x1="16" y1="2" x2="16" y2="6" />
      <line x1="8" y1="2" x2="8" y2="6" />
      <line x1="3" y1="10" x2="21" y2="10" />
    </svg>
  );
}

export function Topbar({ currentUser, onLogout, children }) {
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    if (!open) return;
    function handleOutside(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleOutside);
    return () => document.removeEventListener("mousedown", handleOutside);
  }, [open]);

  const initial = (
    currentUser?.first_name?.[0] ||
    currentUser?.email?.[0] ||
    "U"
  ).toUpperCase();

  const displayName =
    currentUser?.first_name && currentUser?.last_name
      ? `${currentUser.first_name} ${currentUser.last_name}`
      : currentUser?.email || "Usuario";

  return (
    <header className="topbar" role="banner">
      <div className="topbar-inner">

        <div className="topbar-brand">
          <CalendarIcon />
          <span>Sistema de Asignacion</span>
        </div>

        {children && <div className="topbar-nav">{children}</div>}

        <div className="topbar-user" ref={dropdownRef}>
          <button
            type="button"
            className="topbar-avatar"
            onClick={() => setOpen((prev) => !prev)}
            aria-label="Menu de usuario"
            aria-expanded={open}
          >
            {initial}
          </button>

          {open && (
            <div className="topbar-dropdown" role="menu">
              <div className="topbar-dropdown-user">
                <p className="topbar-dropdown-name">{displayName}</p>
                <p className="topbar-dropdown-email">{currentUser?.email}</p>
                <span className="topbar-dropdown-role">{currentUser?.role}</span>
              </div>
              <button
                type="button"
                className="topbar-dropdown-action danger-action"
                role="menuitem"
                onClick={() => {
                  setOpen(false);
                  onLogout();
                }}
              >
                Cerrar sesion
              </button>
            </div>
          )}
        </div>

      </div>
    </header>
  );
}
