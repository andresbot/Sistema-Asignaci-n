import { useEffect, useState } from "react";
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

function WorkspaceOverviewPanel({ currentUser, sectionCount, isAdmin, isCoordinator }) {
  return (
    <section className="panel-card dashboard-card workspace-overview-card">
      <header className="dashboard-header">
        <div>
          <p className="eyebrow">Panel principal</p>
          <h1>Vista general del sistema</h1>
          <p className="lead compact">
            Navega por secciones para mantener separadas las tareas administrativas, la configuracion y la programacion.
          </p>
        </div>
      </header>

      <div className="stack-grid workspace-metrics">
        <article>
          <span>Usuario activo</span>
          <strong>{currentUser?.email || "sin correo"}</strong>
        </article>
        <article>
          <span>Rol</span>
          <strong>{currentUser?.role || "sin rol"}</strong>
        </article>
        <article>
          <span>Secciones visibles</span>
          <strong>{sectionCount}</strong>
        </article>
      </div>

      <div className="workspace-quick-notes">
        <article className="card-block">
          <h2>Orden sugerido</h2>
          <p className="hint">
            {isAdmin
              ? "Inicio, Usuarios, Configuracion e Importacion separan mejor las tareas del administrador."
              : isCoordinator
                ? "Programacion y Configuracion limitada concentran solo lo que el coordinador necesita."
                : "Cada rol recibira sus secciones propias segun permisos."}
          </p>
        </article>
        <article className="card-block">
          <h2>Objetivo visual</h2>
          <p className="hint">
            Cada modulo queda en su propia pantalla interna para que no todo compita en la misma vista.
          </p>
        </article>
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
        apiBaseLabel={coreApiBase}
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
    <main className="app-shell workspace-shell">
      <div className="workspace-layout">
        <aside className="panel-card workspace-sidebar">
          <div>
            <p className="eyebrow">Sistema de asignacion</p>
            <h2>{isAdmin ? "Administrador" : "Coordinador"}</h2>
            <p className="lead compact">{currentUser?.email || "Sesion activa"}</p>
          </div>

          <nav className="workspace-nav" aria-label="Secciones del panel">
            {sectionItems.map((section) => (
              <button
                key={section.key}
                type="button"
                className={
                  section.key === activeSection ? "workspace-nav-item active" : "workspace-nav-item"
                }
                onClick={() => setActiveSection(section.key)}
              >
                {section.label}
              </button>
            ))}
          </nav>

          <div className="workspace-sidebar-footer">
            <button className="ghost" onClick={handleLogout}>
              Cerrar sesion
            </button>
          </div>
        </aside>

        <section className="workspace-content">
          {activeSectionItem?.key === "inicio" ? (
            <WorkspaceOverviewPanel
              currentUser={currentUser}
              sectionCount={sectionItems.length}
              isAdmin={isAdmin}
              isCoordinator={isCoordinator}
            />
          ) : null}

          {activeSectionItem?.key === "horario" ? (
            <ScheduleView
              authToken={authToken}
              periodos={configState.periods?.items ?? []}
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
  );
}

export default App;
