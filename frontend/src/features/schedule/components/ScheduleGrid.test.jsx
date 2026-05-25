import { render, screen } from '@testing-library/react';

import { ScheduleGrid } from './ScheduleGrid';

describe('ScheduleGrid', () => {
  it('renders assignments even when teacher or space data is missing', () => {
    const assignments = [
      {
        id: 1,
        asignatura: { id: 1, code: 'MAT101', name: 'Cálculo I' },
        working_day: { id: 1, day_of_week: 2, name: 'Martes' },
        time_slot: { id: 1, start_time: '08:00', end_time: '10:00', name: 'Mañana' },
        grupo: { id: 1, name: 'Grupo 1' },
        docente: null,
        espacio: null,
      },
    ];

    render(<ScheduleGrid assignments={assignments} />);

    expect(screen.getByText('Cálculo I')).toBeInTheDocument();
    expect(screen.getByText('Sin docente')).toBeInTheDocument();
    expect(screen.getByText(/Grupo 1/i)).toBeInTheDocument();
    expect(screen.getByText(/Sin salón/i)).toBeInTheDocument();
  });
});