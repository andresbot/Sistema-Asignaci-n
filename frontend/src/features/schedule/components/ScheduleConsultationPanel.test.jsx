import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ScheduleConsultationPanel } from './ScheduleConsultationPanel';
import * as scheduleApi from '../services/scheduleApi';

// Mock the scheduleApi module
jest.mock('../services/scheduleApi');

describe('ScheduleConsultationPanel', () => {
  const mockToken = 'test-auth-token';
  const mockCurrentUser = {
    id: 1,
    email: 'test@example.com',
    role: 'docente',
    first_name: 'Test',
    last_name: 'User',
  };
  const mockOnLogout = jest.fn();

  const mockPeriods = [
    {
      id: 1,
      code: '2026-1',
      name: 'Periodo 2026-1',
      start_date: '2026-01-15',
      end_date: '2026-05-30',
      is_schedule_published: false,
    },
    {
      id: 2,
      code: '2026-2',
      name: 'Periodo 2026-2',
      start_date: '2026-07-01',
      end_date: '2026-11-30',
      is_schedule_published: true,
    },
    {
      id: 3,
      code: '2026-3',
      name: 'Periodo 2026-3',
      start_date: '2026-12-01',
      end_date: '2027-03-31',
      is_schedule_published: true,
    },
  ];

  const mockScheduleItems = [
    {
      id: 1,
      subject: {
        id: 1,
        code: 'MAT101',
        name: 'Cálculo I',
      },
      subject_group: {
        id: 1,
        identifier: 'Grupo 1',
      },
      working_day: {
        id: 1,
        day_of_week: 2,
        name: 'Martes',
      },
      time_slot: {
        id: 1,
        start_time: '08:00',
        end_time: '10:00',
      },
      academic_program: {
        id: 1,
        code: 'ING-SIS',
        name: 'Ingeniería de Sistemas',
      },
      teacher: {
        id: 1,
        first_name: 'Juan',
        last_name: 'García',
      },
      semester: 1,
    },
    {
      id: 2,
      subject: {
        id: 2,
        code: 'FIS101',
        name: 'Física I',
      },
      subject_group: {
        id: 2,
        identifier: 'Grupo A',
      },
      working_day: {
        id: 2,
        day_of_week: 4,
        name: 'Jueves',
      },
      time_slot: {
        id: 2,
        start_time: '14:00',
        end_time: '16:00',
      },
      academic_program: {
        id: 1,
        code: 'ING-SIS',
        name: 'Ingeniería de Sistemas',
      },
      teacher: {
        id: 2,
        first_name: 'María',
        last_name: 'López',
      },
      semester: 2,
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Scenario 1: Load periods and select default published period', () => {
    it('should load periods and select the most recent published period by default', async () => {
      scheduleApi.listSchedulePeriods.mockResolvedValue(mockPeriods);
      scheduleApi.fetchMySchedule.mockResolvedValue(mockScheduleItems);

      render(
        <ScheduleConsultationPanel
          authToken={mockToken}
          currentUser={mockCurrentUser}
          onLogout={mockOnLogout}
        />
      );

      // Wait for periods to load
      await waitFor(() => {
        expect(scheduleApi.listSchedulePeriods).toHaveBeenCalledWith(mockToken);
      });

      // Verify that a published period is selected by default
      // The component should select the first published period or the last one in the list
      await waitFor(() => {
        expect(scheduleApi.fetchMySchedule).toHaveBeenCalled();
      });

      // Period 3 (most recent published) should be selected
      expect(scheduleApi.fetchMySchedule).toHaveBeenCalledWith(mockToken, 3);
    });

    it('should render the period select dropdown with all periods', async () => {
      scheduleApi.listSchedulePeriods.mockResolvedValue(mockPeriods);
      scheduleApi.fetchMySchedule.mockResolvedValue([]);

      render(
        <ScheduleConsultationPanel
          authToken={mockToken}
          currentUser={mockCurrentUser}
          onLogout={mockOnLogout}
        />
      );

      await waitFor(() => {
        const periodSelect = screen.getByDisplayValue(/2026-3/);
        expect(periodSelect).toBeInTheDocument();
      });

      // Verify all periods are in the dropdown
      const options = screen.getAllByRole('option');
      expect(options.length).toBeGreaterThanOrEqual(mockPeriods.length);
    });

    it('should display status "Publicado" for selected published period', async () => {
      scheduleApi.listSchedulePeriods.mockResolvedValue(mockPeriods);
      scheduleApi.fetchMySchedule.mockResolvedValue(mockScheduleItems);

      render(
        <ScheduleConsultationPanel
          authToken={mockToken}
          currentUser={mockCurrentUser}
          onLogout={mockOnLogout}
        />
      );

      await waitFor(() => {
        expect(screen.getByText('Publicado')).toBeInTheDocument();
      });
    });
  });

  describe('Scenario 2: Period not published', () => {
    it('should display "not published" message when user selects an unpublished period', async () => {
      scheduleApi.listSchedulePeriods.mockResolvedValue(mockPeriods);
      scheduleApi.fetchMySchedule.mockRejectedValue(
        new Error('El horario de este periodo aun no ha sido publicado.')
      );

      render(
        <ScheduleConsultationPanel
          authToken={mockToken}
          currentUser={mockCurrentUser}
          onLogout={mockOnLogout}
        />
      );

      // Initially shows published period
      await waitFor(() => {
        expect(scheduleApi.listSchedulePeriods).toHaveBeenCalled();
      });

      // Switch to unpublished period (ID 1)
      const select = screen.getByRole('combobox');
      await userEvent.setup().selectOptions(select, '1');

      await waitFor(() => {
        expect(
          screen.getByText(/horario no disponible|horario aún no ha sido publicado/i)
        ).toBeInTheDocument();
      });
    });

    it('should display "Sin publicar" status badge for unpublished periods', async () => {
      const unpublishedPeriods = [
        { ...mockPeriods[0], is_schedule_published: false },
      ];

      scheduleApi.listSchedulePeriods.mockResolvedValue(unpublishedPeriods);
      scheduleApi.fetchMySchedule.mockRejectedValue(
        new Error('El horario de este periodo aun no ha sido publicado.')
      );

      render(
        <ScheduleConsultationPanel
          authToken={mockToken}
          currentUser={mockCurrentUser}
          onLogout={mockOnLogout}
        />
      );

      await waitFor(() => {
        expect(screen.getByText('Sin publicar')).toBeInTheDocument();
      });
    });
  });

  describe('Scenario 3: Schedule display', () => {
    it('should render schedule items for published period', async () => {
      scheduleApi.listSchedulePeriods.mockResolvedValue(mockPeriods);
      scheduleApi.fetchMySchedule.mockResolvedValue(mockScheduleItems);

      render(
        <ScheduleConsultationPanel
          authToken={mockToken}
          currentUser={mockCurrentUser}
          onLogout={mockOnLogout}
        />
      );

      await waitFor(() => {
        expect(screen.getByText('MAT101')).toBeInTheDocument();
        expect(screen.getByText('Cálculo I')).toBeInTheDocument();
      });

      // Verify teacher name is displayed
      expect(screen.getByText(/Juan García/i)).toBeInTheDocument();
    });

    it('should display "No hay registros" when schedule is empty', async () => {
      scheduleApi.listSchedulePeriods.mockResolvedValue(mockPeriods);
      scheduleApi.fetchMySchedule.mockResolvedValue([]);

      render(
        <ScheduleConsultationPanel
          authToken={mockToken}
          currentUser={mockCurrentUser}
          onLogout={mockOnLogout}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/no hay registros/i)).toBeInTheDocument();
      });
    });

    it('should render correct number of schedule cards', async () => {
      scheduleApi.listSchedulePeriods.mockResolvedValue(mockPeriods);
      scheduleApi.fetchMySchedule.mockResolvedValue(mockScheduleItems);

      render(
        <ScheduleConsultationPanel
          authToken={mockToken}
          currentUser={mockCurrentUser}
          onLogout={mockOnLogout}
        />
      );

      await waitFor(() => {
        const cards = screen.getAllByRole('article');
        // At least 2 schedule cards should be rendered
        expect(cards.length).toBeGreaterThanOrEqual(2);
      });
    });

    it('should display all required fields in schedule card', async () => {
      scheduleApi.listSchedulePeriods.mockResolvedValue(mockPeriods);
      scheduleApi.fetchMySchedule.mockResolvedValue([mockScheduleItems[0]]);

      render(
        <ScheduleConsultationPanel
          authToken={mockToken}
          currentUser={mockCurrentUser}
          onLogout={mockOnLogout}
        />
      );

      await waitFor(() => {
        // Subject code
        expect(screen.getByText('MAT101')).toBeInTheDocument();
        // Subject name
        expect(screen.getByText('Cálculo I')).toBeInTheDocument();
        // Group
        expect(screen.getByText(/Grupo 1/)).toBeInTheDocument();
        // Day and time
        expect(screen.getByText(/Martes.*08:00.*10:00/)).toBeInTheDocument();
        // Program
        expect(screen.getByText(/Ingeniería de Sistemas/)).toBeInTheDocument();
        // Teacher
        expect(screen.getByText(/Juan García/)).toBeInTheDocument();
      });
    });
  });

  describe('Scenario 4: Period selection changes', () => {
    it('should fetch schedule when period selection changes', async () => {
      scheduleApi.listSchedulePeriods.mockResolvedValue(mockPeriods);
      scheduleApi.fetchMySchedule.mockResolvedValue(mockScheduleItems);

      render(
        <ScheduleConsultationPanel
          authToken={mockToken}
          currentUser={mockCurrentUser}
          onLogout={mockOnLogout}
        />
      );

      await waitFor(() => {
        expect(scheduleApi.fetchMySchedule).toHaveBeenCalled();
      });

      const select = screen.getByRole('combobox');

      // Change selection to period 2
      await userEvent.setup().selectOptions(select, '2');

      await waitFor(() => {
        expect(scheduleApi.fetchMySchedule).toHaveBeenCalledWith(mockToken, 2);
      });
    });
  });

  describe('Scenario 5: User info and logout', () => {
    it('should display current user role in the header', () => {
      scheduleApi.listSchedulePeriods.mockResolvedValue(mockPeriods);
      scheduleApi.fetchMySchedule.mockResolvedValue([]);

      render(
        <ScheduleConsultationPanel
          authToken={mockToken}
          currentUser={mockCurrentUser}
          onLogout={mockOnLogout}
        />
      );

      expect(screen.getByText(/docente/i)).toBeInTheDocument();
    });

    it('should call onLogout when logout button is clicked', async () => {
      scheduleApi.listSchedulePeriods.mockResolvedValue(mockPeriods);
      scheduleApi.fetchMySchedule.mockResolvedValue([]);

      render(
        <ScheduleConsultationPanel
          authToken={mockToken}
          currentUser={mockCurrentUser}
          onLogout={mockOnLogout}
        />
      );

      const logoutButton = screen.getByRole('button', { name: /cerrar sesion/i });
      await userEvent.click(logoutButton);

      expect(mockOnLogout).toHaveBeenCalled();
    });
  });

  describe('Error handling', () => {
    it('should display error message on API failure', async () => {
      scheduleApi.listSchedulePeriods.mockRejectedValue(
        new Error('Network error')
      );

      render(
        <ScheduleConsultationPanel
          authToken={mockToken}
          currentUser={mockCurrentUser}
          onLogout={mockOnLogout}
        />
      );

      await waitFor(() => {
        expect(
          screen.getByText(/no se pudieron cargar los periodos/i)
        ).toBeInTheDocument();
      });
    });

    it('should show loading state while fetching schedule', async () => {
      scheduleApi.listSchedulePeriods.mockResolvedValue(mockPeriods);
      scheduleApi.fetchMySchedule.mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      render(
        <ScheduleConsultationPanel
          authToken={mockToken}
          currentUser={mockCurrentUser}
          onLogout={mockOnLogout}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/cargando horario/i)).toBeInTheDocument();
      });
    });
  });
});
