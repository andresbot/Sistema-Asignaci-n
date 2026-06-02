import { useEffect, useState } from "react";
import { ToastProvider } from "./shared/components/Toast";
import { Topbar } from "./shared/components/Topbar";
import { LoginPanel } from "./features/auth/components/LoginPanel";
import {
  RoleHomeView,
  SessionLoadingView,
} from "./features/auth/components/SessionStateView";
import { useAuthSession } from "./features/auth/hooks/useAuthSession";
import { ImportManagementPanel } from "./features/config/components/ImportManagementPanel";
import { SystemConfigPanel } from "./features/config/components/SystemConfigPanel";
import { useSystemConfig } from "./features/config/hooks/useSystemConfig";
import { ScheduleConsultationPanel } from "./features/schedule/components/ScheduleConsultationPanel";
import { ScheduleView } from "./features/schedule/components/ScheduleView";
import { UsersDashboard } from "./features/users/components/UsersDashboard";
import { useUsersManagement } from "./features/users/hooks/useUsersManagement";
import { coreApiBase } from "./shared/api/coreApiClient";

function NavIcon({ children }) {
  return (
    <svg
      width="17"
      height="17"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.9"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      className="nav-icon"
    >
      {children}
    </svg>
  );
}

const ICONS = {
  inicio: (
    <NavIcon>
      <rect x="3" y="3" width="7" height="7" rx="1.5" />
      <rect x="14" y="3" width="7" height="7" rx="1.5" />
      <rect x="3" y="14" width="7" height="7" rx="1.5" />
      <rect x="14" y="14" width="7" height="7" rx="1.5" />
    </NavIcon>
  ),
  horario: (
    <NavIcon>
      <rect x="3" y="4" width="18" height="18" rx="2" />
      <line x1="16" y1="2" x2="16" y2="6" />
      <line x1="8" y1="2" x2="8" y2="6" />
      <line x1="3" y1="10" x2="21" y2="10" />
    </NavIcon>
  ),
  usuarios: (
    <NavIcon>
      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </NavIcon>
  ),
  configuracion: (
    <NavIcon>
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
    </NavIcon>
  ),
  importacion: (
    <NavIcon>
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="17 8 12 3 7 8" />
      <line x1="12" y1="3" x2="12" y2="15" />
    </NavIcon>
  ),
  programacion: (
    <NavIcon>
      <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2" />
      <rect x="9" y="3" width="6" height="4" rx="2" />
      <line x1="9" y1="12" x2="15" y2="12" />
      <line x1="9" y1="16" x2="13" y2="16" />
    </NavIcon>
  ),
};

const ADMIN_SECTIONS = [
  { key: "inicio", label: "Inicio" },
  { key: "horario", label: "Horario" },
  { key: "usuarios", label: "Usuarios" },
  { key: "configuracion", label: "Configuracion" },
  { key: "importacion", label: "Importacion" },
];

const COORDINATOR_SECTIONS = [
  { key: "inicio", label: "Inicio" },
  { key: "programacion", label: "Programacion" },
  { key: "configuracion", label: "Configuracion" },
];

function MetricCard({ icon, value, label, loading }) {
  return (
    <article className="metric-card">
      <div className="metric-card-icon">{icon}</div>
      <strong className="metric-card-value">{loading ? "—" : value}</strong>
      <span className="metric-card-label">{label}</span>
    </article>
  );
}

function WorkspaceOverviewPanel({ currentUser, isAdmin, configState, onNavigate }) {
  const hour = new Date().getHours();
  const greeting =
    hour < 12 ? "Buenos dias" : hour < 19 ? "Buenas tardes" : "Buenas noches";
  const firstName =
    currentUser?.first_name ||
    currentUser?.email?.split("@")[0] ||
    "usuario";

  const periods      = configState?.periods?.items ?? [];
  const classrooms   = configState?.classrooms?.items ?? [];
  const teachers     = configState?.teachers?.items ?? [];
  const subjects     = configState?.subjects?.items ?? [];
  const offerings    = configState?.subjectOfferings?.items ?? [];

  const activePeriod    = periods[0] ?? null;
  const schedulePublished = activePeriod?.is_schedule_published === true;

  const isLoading =
    configState?.classrooms?.loading ||
    configState?.teachers?.loading ||
    configState?.subjects?.loading;

  return (
    <section className="panel-card dashboard-card workspace-overview-card">
      <header className="page-header">
        <div>
          <h1 className="page-title">{greeting}, {firstName}</h1>
          <p className="page-subtitle">
            {isAdmin ? "Administrador del sistema" : "Coordinador academico"}
          </p>
        </div>
      </header>

      <div className="metrics-grid">
        <MetricCard
          loading={isLoading}
          value={classrooms.length}
          label="Salones"
          icon={
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 21h18M3 10.5V21M21 10.5V21M3 10.5L12 3l9 7.5"/>
              <rect x="9" y="14" width="6" height="7" />
            </svg>
          }
        />
        <MetricCard
          loading={isLoading}
          value={teachers.length}
          label="Docentes"
          icon={
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          }
        />
        <MetricCard
          loading={isLoading}
          value={subjects.length}
          label="Asignaturas"
          icon={
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
            </svg>
          }
        />
        <MetricCard
          loading={isLoading}
          value={offerings.length}
          label="Ofertas"
          icon={
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <line x1="8" y1="6" x2="21" y2="6"/>
              <line x1="8" y1="12" x2="21" y2="12"/>
              <line x1="8" y1="18" x2="21" y2="18"/>
              <line x1="3" y1="6" x2="3.01" y2="6"/>
              <line x1="3" y1="12" x2="3.01" y2="12"/>
              <line x1="3" y1="18" x2="3.01" y2="18"/>
            </svg>
          }
        />
      </div>

      <div className="period-status-block">
        {activePeriod ? (
          <>
            <div className="period-status-info">
              <p className="eyebrow">Periodo activo</p>
              <h3>{activePeriod.name}</h3>
              <div className="period-status-meta">
                <span>{activePeriod.start_date} — {activePeriod.end_date}</span>
                <span className={`status-pill ${schedulePublished ? "success" : "warning"}`}>
                  {schedulePublished ? "Horario publicado" : "Sin publicar"}
                </span>
              </div>
            </div>
            <button type="button" onClick={() => onNavigate(isAdmin ? "horario" : "programacion")}>
              {isAdmin ? "Ver horario" : "Ver programacion"} →
            </button>
          </>
        ) : (
          <>
            <div className="period-status-info">
              <p className="eyebrow">Periodo activo</p>
              <h3 className="period-status-empty">Sin periodo activo configurado</h3>
            </div>
            <button type="button" className="secondary" onClick={() => onNavigate("configuracion")}>
              Configurar periodos
            </button>
          </>
        )}
      </div>
    </section>
  );
}

function App() {
  const {
    authToken,
    currentUser,
    authLoading,
    loginState,
    setLoginState,
    handleLogin,
    handleLogout,
  } = useAuthSession();

  const isAdmin = Boolean(authToken && currentUser?.role === "administrador");
  const isCoordinator = Boolean(authToken && currentUser?.role === "coordinador");
  const isTeacherOrStudent = Boolean(
    authToken && (currentUser?.role === "docente" || currentUser?.role === "estudiante"),
  );
  const canUseProgrammingConfig = isAdmin || isCoordinator;

  const {
    roles,
    users,
    usersLoading,
    usersError,
    formMode,
    formState,
    selectedUser,
    setFormState,
    loadUsersAndRoles,
    resetFormToCreate,
    handleSelectEdit,
    handleSubmitForm,
    handleDeactivateUser,
  } = useUsersManagement({
    authToken,
    enabled: isAdmin,
  });

  const {
    configState,
    importState,
    refreshAll,
    handleFieldChange,
    handleDownloadTemplate,
    handleImportFieldChange,
    handleImportSubmit,
    handleSelectEdit: handleConfigSelectEdit,
    handleDelete,
    handleSubmit,
    handlePublishPeriod,
    handleUnpublishPeriod,
    resetResourceForm,
  } = useSystemConfig({
    authToken,
    enabled: canUseProgrammingConfig,
    role: currentUser?.role,
  });

  const sectionItems = isAdmin ? ADMIN_SECTIONS : isCoordinator ? COORDINATOR_SECTIONS : [];
  const defaultSection = sectionItems[0]?.key || "inicio";
  const [activeSection, setActiveSection] = useState(defaultSection);

  useEffect(() => {
    setActiveSection(defaultSection);
  }, [defaultSection]);

  const activeSectionItem =
    sectionItems.find((section) => section.key === activeSection) || sectionItems[0];

  const handleFormChange = (field, value) => {
    setFormState((previous) => ({
      ...previous,
      [field]: value,
    }));
  };

  if (authLoading) {
    return <SessionLoadingView />;
  }

  if (!authToken) {
    return (
      <LoginPanel
        loginState={loginState}
        setLoginState={setLoginState}
        onSubmit={handleLogin}
      />
    );
  }

  if (isTeacherOrStudent) {
    return (
      <ScheduleConsultationPanel
        authToken={authToken}
        currentUser={currentUser}
        onLogout={handleLogout}
      />
    );
  }

  if (!canUseProgrammingConfig) {
    return <RoleHomeView currentUser={currentUser} onLogout={handleLogout} />;
  }

  return (
    <ToastProvider>
    <Topbar currentUser={currentUser} onLogout={handleLogout}>
      {sectionItems.map((section) => (
        <button
          key={section.key}
          type="button"
          className={
            section.key === activeSection ? "workspace-nav-item active" : "workspace-nav-item"
          }
          onClick={() => setActiveSection(section.key)}
        >
          {ICONS[section.key] ?? null}
          {section.label}
        </button>
      ))}
    </Topbar>

    <main className="app-shell workspace-shell">
      <div className="workspace-layout">
        <section className="workspace-content">
          {activeSectionItem?.key === "inicio" ? (
            <WorkspaceOverviewPanel
              currentUser={currentUser}
              isAdmin={isAdmin}
              configState={configState}
              onNavigate={setActiveSection}
            />
          ) : null}

          {activeSectionItem?.key === "horario" ? (
            <ScheduleView
              authToken={authToken}
              periodos={configState.periods?.items ?? []}
              canRunExecution={isAdmin}
            />
          ) : null}

          {activeSectionItem?.key === "usuarios" ? (
            <UsersDashboard
              currentUser={currentUser}
              formMode={formMode}
              formState={formState}
              roles={roles}
              selectedUser={selectedUser}
              users={users}
              usersLoading={usersLoading}
              usersError={usersError}
              onRefresh={loadUsersAndRoles}
              onLogout={handleLogout}
              onFormChange={handleFormChange}
              onFormSubmit={handleSubmitForm}
              onCancelEdit={resetFormToCreate}
              onSelectEdit={handleSelectEdit}
              onDeactivate={handleDeactivateUser}
            />
          ) : null}

          {activeSectionItem?.key === "programacion" ? (
            <SystemConfigPanel
              configState={configState}
              onRefresh={refreshAll}
              onFieldChange={handleFieldChange}
              onSubmit={handleSubmit}
              onEdit={handleConfigSelectEdit}
              onDelete={handleDelete}
              onCancel={resetResourceForm}
              onPublishPeriod={handlePublishPeriod}
              onUnpublishPeriod={handleUnpublishPeriod}
              visibleSections={["subjectOfferings"]}
              title="Programacion academica"
              description="Gestiona solo la programacion de asignaturas para este rol."
              showImportSection={false}
            />
          ) : null}

          {activeSectionItem?.key === "configuracion" ? (
            <SystemConfigPanel
              configState={configState}
              onRefresh={refreshAll}
              onFieldChange={handleFieldChange}
              onSubmit={handleSubmit}
              onEdit={handleConfigSelectEdit}
              onDelete={handleDelete}
              onCancel={resetResourceForm}
              onPublishPeriod={handlePublishPeriod}
              onUnpublishPeriod={handleUnpublishPeriod}
              visibleSections={isAdmin ? undefined : ["periods", "workingDays", "timeSlots"]}
              title={isAdmin ? "Configuracion general del sistema" : "Configuracion limitada"}
              description={
                isAdmin
                  ? "Aqui se administran los catalogos y recursos maestros del sistema."
                  : "Este espacio muestra solo los parametros que apoyan la programacion."
              }
              showImportSection={false}
            />
          ) : null}

          {isAdmin && activeSectionItem?.key === "importacion" ? (
            <ImportManagementPanel
              importState={importState}
              onDownloadTemplate={handleDownloadTemplate}
              onImportFieldChange={handleImportFieldChange}
              onImportSubmit={handleImportSubmit}
            />
          ) : null}
        </section>
      </div>
    </main>
    </ToastProvider>
  );
}

export default App;
