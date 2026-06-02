function CalendarIcon({ size = 24 }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <rect x="3" y="4" width="18" height="18" rx="2" />
      <line x1="16" y1="2" x2="16" y2="6" />
      <line x1="8" y1="2" x2="8" y2="6" />
      <line x1="3" y1="10" x2="21" y2="10" />
    </svg>
  );
}

export function LoginPanel({ loginState, setLoginState, onSubmit }) {
  return (
    <main className="login-shell">
      <div className="login-brand-panel" aria-hidden="true">
        <div className="login-brand-bg-icon">
          <CalendarIcon size={320} />
        </div>
        <div className="login-brand-content">
          <div className="login-brand-logo">
            <CalendarIcon size={26} />
          </div>
          <h2 className="login-brand-title">
            Sistema de Asignacion de Salones
          </h2>
          <p className="login-brand-tagline">
            Gestiona horarios, espacios y docentes de forma centralizada y eficiente.
          </p>
        </div>
      </div>

      <div className="login-form-panel">
        <div className="login-form-container">
          <div className="login-form-header">
            <span className="login-form-icon">
              <CalendarIcon size={20} />
            </span>
            <p className="eyebrow" style={{ margin: 0 }}>Sistema de Asignacion</p>
          </div>

          <h1 className="login-form-title">Bienvenido de nuevo</h1>
          <p className="login-form-subtitle">
            Ingresa tus credenciales para acceder al panel.
          </p>

          <form className="form-grid login-form" onSubmit={onSubmit}>
            <label>
              Correo electronico
              <input
                type="email"
                value={loginState.email}
                placeholder="usuario@institucion.edu"
                autoComplete="email"
                required
                onChange={(e) =>
                  setLoginState((prev) => ({ ...prev, email: e.target.value }))
                }
              />
            </label>

            <label>
              Contrasena
              <input
                type="password"
                value={loginState.password}
                placeholder="••••••••"
                autoComplete="current-password"
                required
                onChange={(e) =>
                  setLoginState((prev) => ({ ...prev, password: e.target.value }))
                }
              />
            </label>

            {loginState.error ? (
              <div className="login-error-block">
                <p className="error-text" style={{ margin: 0 }}>{loginState.error}</p>
              </div>
            ) : null}

            <button type="submit" disabled={loginState.loading} className="login-submit-btn">
              {loginState.loading ? "Ingresando..." : "Iniciar sesion"}
            </button>
          </form>
        </div>
      </div>
    </main>
  );
}
