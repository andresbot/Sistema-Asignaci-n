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
    <form className="form-grid" onSubmit={onSubmit}>
      <label>
        Correo
        <input
          type="email"
          value={formState.email}
          onChange={(e) => onChange("email", e.target.value)}
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
            onChange={(e) => onChange("password", e.target.value)}
            required
          />
        </label>
      ) : null}

      <div className="form-row">
        <label>
          Nombre
          <input
            type="text"
            value={formState.first_name}
            onChange={(e) => onChange("first_name", e.target.value)}
            placeholder="Juan"
            required
          />
        </label>
        <label>
          Apellido
          <input
            type="text"
            value={formState.last_name}
            onChange={(e) => onChange("last_name", e.target.value)}
            placeholder="Perez"
            required
          />
        </label>
      </div>

      <label>
        Rol
        <select
          value={formState.role_id}
          onChange={(e) => onChange("role_id", e.target.value)}
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
          onChange={(e) => onChange("is_active", e.target.checked)}
        />
        Usuario activo
      </label>

      {formState.error ? <p className="error-text">{formState.error}</p> : null}

      <div className="actions-inline">
        <button type="submit" disabled={formState.submitting}>
          {formState.submitting
            ? "Guardando..."
            : formMode === "create"
              ? "Crear usuario"
              : "Guardar cambios"}
        </button>
        <button type="button" className="secondary" onClick={onCancelEdit}>
          Cancelar
        </button>
      </div>
    </form>
  );
}
