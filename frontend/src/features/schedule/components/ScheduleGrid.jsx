function ScheduleCell({ asignaciones }) {
  if (!asignaciones || asignaciones.length === 0) {
    return <td className="schedule-cell schedule-cell--empty" />;
  }

  return (
    <td className="schedule-cell">
      {asignaciones.map((a) => (
        <div key={a.id} className="schedule-chip">
          <strong className="schedule-chip__subject">{a.asignatura.name}</strong>
          <span className="schedule-chip__meta">
            {a.docente.first_name} {a.docente.last_name}
          </span>
          <span className="schedule-chip__meta">
            {a.grupo.name} &middot; {a.espacio.name}
          </span>
        </div>
      ))}
    </td>
  );
}

export function ScheduleGrid({ assignments }) {
  if (!assignments || assignments.length === 0) {
    return (
      <p className="hint" style={{ textAlign: "center", padding: "32px 0" }}>
        No hay asignaciones para los filtros seleccionados.
      </p>
    );
  }

  // Build unique sorted days and slots from the assignments
  const daysMap = new Map();
  const slotsMap = new Map();

  for (const a of assignments) {
    const d = a.working_day;
    const s = a.time_slot;
    if (!daysMap.has(d.id)) daysMap.set(d.id, d);
    if (!slotsMap.has(s.id)) slotsMap.set(s.id, s);
  }

  const days = [...daysMap.values()].sort((a, b) => a.day_of_week - b.day_of_week);
  const slots = [...slotsMap.values()].sort((a, b) =>
    a.start_time.localeCompare(b.start_time)
  );

  // Index: slotId -> dayId -> [assignments]
  const grid = new Map();
  for (const a of assignments) {
    const key = `${a.time_slot.id}-${a.working_day.id}`;
    if (!grid.has(key)) grid.set(key, []);
    grid.get(key).push(a);
  }

  return (
    <div className="schedule-table-wrap">
      <table className="schedule-table">
        <thead>
          <tr>
            <th className="schedule-th-slot">Franja</th>
            {days.map((d) => (
              <th key={d.id} className="schedule-th-day">
                {d.name}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {slots.map((slot) => (
            <tr key={slot.id}>
              <td className="schedule-td-slot">
                <strong>{slot.name}</strong>
                <span className="hint small" style={{ display: "block" }}>
                  {slot.start_time.slice(0, 5)} – {slot.end_time.slice(0, 5)}
                </span>
              </td>
              {days.map((day) => (
                <ScheduleCell
                  key={day.id}
                  asignaciones={grid.get(`${slot.id}-${day.id}`)}
                />
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
