export function UnassignedList({ unassigned }) {
  if (!unassigned || unassigned.length === 0) return null;

  return (
    <section className="card-block unassigned-section">
      <h2 className="unassigned-title">
        Asignaturas no asignadas
        <span className="badge muted" style={{ marginLeft: 10 }}>
          {unassigned.length}
        </span>
      </h2>
      <p className="hint" style={{ marginTop: 0, marginBottom: 14 }}>
        Las siguientes asignaturas no pudieron ser asignadas por el algoritmo.
      </p>
      <ul className="unassigned-list">
        {unassigned.map((item) => (
          <li key={item.id} className="unassigned-item">
            <div className="unassigned-item__header">
              <strong>{item.asignatura.name}</strong>
              <span className="badge muted">{item.asignatura.code}</span>
              <span className="hint small">&mdash; Grupo: {item.grupo.name}</span>
            </div>
            <p className="unassigned-item__reason">{item.razon}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
