import { UserFormPanel } from "./UserFormPanel";
import { UsersTablePanel } from "./UsersTablePanel";

export function UsersDashboard({
  currentUser,
  formMode,
  formState,
  roles,
  selectedUser,
  users,
  usersLoading,
  usersError,
  onRefresh,
  onLogout,
  onFormChange,
  onFormSubmit,
  onCancelEdit,
  onSelectEdit,
  onDeactivate,
}) {
  return (
    <section className="panel-card dashboard-card users-dashboard-card">
      <header className="dashboard-header">
        <div>
          <p className="eyebrow"></p>
          <h1>Gestion de usuarios por rol</h1>
          <p className="lead compact">
            Sesion activa: {currentUser?.email} ({currentUser?.role})
          </p>
        </div>
        <div className="actions-inline">
          <button className="secondary" onClick={onRefresh}>
            Recargar
          </button>
          <button className="ghost" onClick={onLogout}>
            Cerrar sesion
          </button>
        </div>
      </header>

      <div className="dashboard-grid">
        <UserFormPanel
          formMode={formMode}
          formState={formState}
          selectedUser={selectedUser}
          roles={roles}
          onChange={onFormChange}
          onSubmit={onFormSubmit}
          onCancelEdit={onCancelEdit}
        />

        <UsersTablePanel
          users={users}
          usersLoading={usersLoading}
          usersError={usersError}
          onEdit={onSelectEdit}
          onDeactivate={onDeactivate}
        />
      </div>
    </section>
  );
}
