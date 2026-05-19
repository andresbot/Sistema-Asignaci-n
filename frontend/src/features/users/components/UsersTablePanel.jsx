export function UsersTablePanel({ users, usersLoading, usersError, onEdit, onDeactivate }) {
  return (
    <section className="card-block">
      <h2>Usuarios registrados</h2>
      {usersError ? <p className="error-text">{usersError}</p> : null}
      {usersLoading ? <p className="hint">Cargando usuarios...</p> : null}

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Correo</th>
              <th>Rol</th>
              <th>Estado</th>
              <th>Acciones</th>
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
                  <div className="actions-inline compact">
                    <button className="secondary" type="button" onClick={() => onEdit(user)}>
                      Editar
                    </button>
                    {user.is_active ? (
                      <button className="danger" type="button" onClick={() => onDeactivate(user)}>
                        Desactivar
                      </button>
                    ) : null}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
