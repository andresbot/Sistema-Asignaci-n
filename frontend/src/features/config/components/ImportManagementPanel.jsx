export function ImportManagementPanel({
  importState,
  onDownloadTemplate,
  onImportFieldChange,
  onImportSubmit,
}) {
  return (
    <section className="card-block system-config-panel">
      <header className="dashboard-header config-header">
        <div>
          <p className="eyebrow"></p>
          <h2>Importacion masiva</h2>
          <p className="lead compact">
            Sube archivos CSV o XLSX para cargar datos maestros sin abrir la pantalla de configuracion.
          </p>
        </div>
      </header>

      <article className="card-block config-card">
        <form className="form-grid" onSubmit={onImportSubmit}>
          <label>
            Tipo de dato maestro
            <select
              value={importState.selectedResourceType}
              onChange={(event) =>
                onImportFieldChange("selectedResourceType", event.target.value)
              }
            >
              {importState.templates.map((template) => (
                <option key={template.resource_type} value={template.resource_type}>
                  {template.resource_type}
                </option>
              ))}
            </select>
          </label>

          <label>
            Archivo CSV/XLSX
            <input
              type="file"
              accept=".csv,.xlsx"
              onChange={(event) =>
                onImportFieldChange("file", event.target.files?.[0] || null)
              }
            />
          </label>

          {importState.error ? <p className="error-text">{importState.error}</p> : null}

          <div className="actions-inline">
            <button type="button" className="secondary" onClick={onDownloadTemplate}>
              Descargar plantilla CSV
            </button>
            <button type="submit" disabled={importState.submitting}>
              {importState.submitting ? "Importando..." : "Importar"}
            </button>
          </div>
        </form>

        {importState.result ? (
          <div className="config-items-list">
            <p className="hint">
              Total: {importState.result.total_processed} | Exitosos: {importState.result.successful} |
              Fallidos: {importState.result.failed}
            </p>

            {importState.result.rows.map((row) => (
              <div key={`${row.row}-${row.status}-${row.message}`} className="config-item-row">
                <div>
                  <strong>Fila {row.row}</strong>
                  <p className="hint small">
                    {row.status === "success" ? "OK" : "Error"}: {row.message}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : null}
      </article>
    </section>
  );
}
