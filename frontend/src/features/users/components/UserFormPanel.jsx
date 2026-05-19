export function UserFormPanel({
  formMode,
  formState,
  selectedUser,
  roles,
  onChange,
  onSubmit,
  onCancelEdit,
}) {
  return (
    <section className="card-block">
      <h2>{formMode === "create" ? "Crear usuario" : "Editar usuario"}</h2>

      <form className="form-grid" onSubmit={onSubmit}>
        <label>
          Correo
          <input
            type="email"
            value={formState.email}
            onChange={(event) => onChange("email", event.target.value)}
            required
          />
        </label>

        {formMode === "create" ? (
          <label>
            Contrasena
            <input
              type="password"
              minLength={8}
              value={formState.password}
              onChange={(event) => onChange("password", event.target.value)}
              required
            />
          </label>
        ) : null}

        <label>
          Nombre
          <input
            type="text"
            value={formState.first_name}
            onChange={(event) => onChange("first_name", event.target.value)}
            required
          />
        </label>

        <label>
          Apellido
          <input
            type="text"
            value={formState.last_name}
            onChange={(event) => onChange("last_name", event.target.value)}
            required
          />
        </label>

        <label>
          Rol
          <select
            value={formState.role_id}
            onChange={(event) => onChange("role_id", event.target.value)}
            required
          >
            <option value="" disabled>
              Selecciona un rol
            </option>
            {roles.map((role) => (
              <option key={role.id} value={role.id}>
                {role.name}
              </option>
            ))}
          </select>
        </label>

        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={formState.is_active}
            onChange={(event) => onChange("is_active", event.target.checked)}
          />
          Usuario activo
        </label>

        {formState.error ? <p className="error-text">{formState.error}</p> : null}

        <div className="actions-inline">
          <button type="submit" disabled={formState.submitting}>
            {formState.submitting
              ? "Guardando..."
              : formMode === "create"
                ? "Crear"
                : "Guardar cambios"}
          </button>

          {formMode === "edit" ? (
            <button type="button" className="secondary" onClick={onCancelEdit}>
              Cancelar edicion
            </button>
          ) : null}
        </div>
      </form>

      {selectedUser ? (
        <p className="hint">
          Editando: {selectedUser.first_name} {selectedUser.last_name}
        </p>
      ) : null}
    </section>
  );
}
