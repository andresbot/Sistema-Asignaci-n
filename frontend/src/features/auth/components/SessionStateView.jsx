export function SessionLoadingView() {
  return (
    <main className="app-shell">
      <section className="panel-card centered">
        <p className="eyebrow">Cargando sesion</p>
        <h1>Validando autenticacion...</h1>
      </section>
    </main>
  );
}

const ROLE_TITLES = {
  administrador: "Panel de Administrador",
  coordinador: "Panel de Coordinador",
  docente: "Panel de Docente",
  estudiante: "Panel de Estudiante",
};

const ROLE_DESCRIPTIONS = {
  administrador:
    "Tienes acceso total al modulo de gestion de usuarios y configuracion del sistema.",
  coordinador:
    "Tu sesion esta activa. En el siguiente incremento habilitaremos tu modulo de programacion academica.",
  docente:
    "Tu sesion esta activa. En el siguiente incremento habilitaremos la consulta de horario docente.",
  estudiante:
    "Tu sesion esta activa. En el siguiente incremento habilitaremos la consulta de horario estudiantil.",
};

export function RoleHomeView({ currentUser, onLogout }) {
  const role = currentUser?.role || "sin rol";
  const title = ROLE_TITLES[role] || "Panel de Usuario";
  const description =
    ROLE_DESCRIPTIONS[role] ||
    "Tu sesion esta activa. Este rol sera habilitado con vistas especificas en los siguientes incrementos.";

  return (
    <main className="app-shell">
      <section className="panel-card role-home-card">
        <p className="eyebrow">Ingreso exitoso</p>
        <h1>{title}</h1>
        <p className="lead">{description}</p>

        <div className="role-home-meta">
          <article>
            <span>Usuario</span>
            <strong>{currentUser?.email || "sin correo"}</strong>
          </article>
          <article>
            <span>Rol activo</span>
            <strong>{role}</strong>
          </article>
          <article>
            <span>Estado</span>
            <strong>Autenticado</strong>
          </article>
        </div>

        <div className="actions-inline">
          <button className="ghost" onClick={onLogout}>
            Cerrar sesion
          </button>
        </div>
      </section>
    </main>
  );
}
