import { createContext, useCallback, useContext, useRef, useState } from "react";
import { createPortal } from "react-dom";

const ToastContext = createContext(null);

const ICONS = {
  success: "✓",
  error: "✕",
  info: "i",
};

function ToastItem({ id, type, message, onRemove }) {
  return (
    <div className={`toast toast--${type}`} role="alert">
      <span className="toast-icon" aria-hidden="true">{ICONS[type]}</span>
      <p className="toast-message">{message}</p>
      <button
        type="button"
        className="toast-close"
        onClick={() => onRemove(id)}
        aria-label="Cerrar notificacion"
      >
        ✕
      </button>
    </div>
  );
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const idRef = useRef(0);

  const remove = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const add = useCallback(
    (type, message) => {
      const id = ++idRef.current;
      setToasts((prev) => [...prev, { id, type, message }]);
      setTimeout(() => remove(id), 4200);
    },
    [remove],
  );

  const toast = {
    success: (msg) => add("success", msg),
    error: (msg) => add("error", msg),
    info: (msg) => add("info", msg),
  };

  return (
    <ToastContext.Provider value={toast}>
      {children}
      {createPortal(
        <div className="toast-container" aria-live="polite" aria-atomic="false">
          {toasts.map((t) => (
            <ToastItem key={t.id} {...t} onRemove={remove} />
          ))}
        </div>,
        document.body,
      )}
    </ToastContext.Provider>
  );
}

export function useToast() {
  return useContext(ToastContext);
}
