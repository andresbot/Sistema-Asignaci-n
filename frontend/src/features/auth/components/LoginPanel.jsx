export function LoginPanel({ apiBaseLabel, loginState, setLoginState, onSubmit }) {
  return (
    <main className="app-shell auth-shell">
      <section className="panel-card auth-card">
        <p className="eyebrow">Gestion de usuarios</p>
        <h1>Inicia sesion</h1>
        <p className="lead">
          Esta vista consume la API de Django para crear, editar y desactivar cuentas por rol.
        </p>

        <form className="form-grid" onSubmit={onSubmit}>
          <label>
            Correo
            <input
              type="email"
              value={loginState.email}
              onChange={(event) =>
                setLoginState((previous) => ({ ...previous, email: event.target.value }))
              }
              required
            />
          </label>

          <label>
            Contrasena
            <input
              type="password"
              value={loginState.password}
              onChange={(event) =>
                setLoginState((previous) => ({
                  ...previous,
                  password: event.target.value,
                }))
              }
              required
            />
          </label>

          {loginState.error ? <p className="error-text">{loginState.error}</p> : null}

          <button type="submit" disabled={loginState.loading}>
            {loginState.loading ? "Ingresando..." : "Iniciar sesion"}
          </button>
        </form>

        <p className="hint">API: {apiBaseLabel}</p>
      </section>
    </main>
  );
}
