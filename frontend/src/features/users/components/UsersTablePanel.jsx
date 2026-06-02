import { EmptyState, EmptyUsersIcon } from "../../../shared/components/EmptyState";
import { RowMenu } from "../../../shared/components/RowMenu";

export function UsersTablePanel({ users, usersLoading, usersError, onEdit, onDeactivate }) {
  return (
    <section className="card-block">
      <h2>Usuarios registrados</h2>

      {usersError ? <p className="error-text">{usersError}</p> : null}

      {usersLoading ? (
        <div className="table-skeleton">
          <div className="table-skeleton-row" />
          <div className="table-skeleton-row" />
          <div className="table-skeleton-row" />
        </div>
      ) : users.length === 0 ? (
        <EmptyState
          icon={<EmptyUsersIcon />}
          title="Sin usuarios registrados"
          description='Usa el boton "+ Nuevo usuario" para agregar el primero.'
        />
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Correo</th>
                <th>Rol</th>
                <th>Estado</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id}>
                  <td>
                    {user.first_name} {user.last_name}
                  </td>
                  <td>{user.email}</td>
                  <td>{user.role.name}</td>
                  <td>
                    <span className={user.is_active ? "badge ok" : "badge muted"}>
                      {user.is_active ? "Activo" : "Inactivo"}
                    </span>
                  </td>
                  <td>
                    <RowMenu
                      items={[
                        { label: "Editar", onClick: () => onEdit(user) },
                        user.is_active
                          ? { label: "Desactivar", onClick: () => onDeactivate(user), danger: true }
                          : null,
                      ]}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
