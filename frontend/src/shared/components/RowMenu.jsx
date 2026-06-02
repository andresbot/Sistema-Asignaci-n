import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

export function RowMenu({ items }) {
  const [open, setOpen] = useState(false);
  const [pos, setPos] = useState({ top: 0, right: 0 });
  const triggerRef = useRef(null);
  const dropdownRef = useRef(null);

  function handleOpen() {
    if (!triggerRef.current) return;
    const rect = triggerRef.current.getBoundingClientRect();
    setPos({
      top: rect.bottom + 6,
      right: window.innerWidth - rect.right,
    });
    setOpen((prev) => !prev);
  }

  useEffect(() => {
    if (!open) return;
    function handleOutside(e) {
      if (
        triggerRef.current?.contains(e.target) ||
        dropdownRef.current?.contains(e.target)
      ) return;
      setOpen(false);
    }
    function handleKey(e) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("mousedown", handleOutside);
    document.addEventListener("keydown", handleKey);
    return () => {
      document.removeEventListener("mousedown", handleOutside);
      document.removeEventListener("keydown", handleKey);
    };
  }, [open]);

  const visibleItems = items.filter(Boolean);

  return (
    <div className="row-menu">
      <button
        ref={triggerRef}
        type="button"
        className="row-menu-trigger"
        onClick={handleOpen}
        aria-label="Acciones"
        aria-expanded={open}
        aria-haspopup="menu"
      >
        ⋮
      </button>

      {open &&
        createPortal(
          <div
            ref={dropdownRef}
            className="row-menu-dropdown"
            role="menu"
            style={{ top: pos.top, right: pos.right }}
          >
            {visibleItems.map((item, i) => (
              <button
                key={i}
                type="button"
                className={`row-menu-item${item.danger ? " row-menu-item--danger" : ""}`}
                role="menuitem"
                disabled={item.disabled}
                onClick={() => {
                  setOpen(false);
                  item.onClick();
                }}
              >
                {item.label}
              </button>
            ))}
          </div>,
          document.body,
        )}
    </div>
  );
}
