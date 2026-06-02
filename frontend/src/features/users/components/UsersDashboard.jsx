import { useEffect, useRef, useState } from "react";
import { Modal } from "../../../shared/components/Modal";
import { useToast } from "../../../shared/components/Toast";
import { UserFormPanel } from "./UserFormPanel";
import { UsersTablePanel } from "./UsersTablePanel";

export function UsersDashboard({
  currentUser,
  formMode,
  formState,
  roles,
  selectedUser,
  users,
  usersLoading,
  usersError,
  onRefresh,
  onFormChange,
  onFormSubmit,
  onCancelEdit,
  onSelectEdit,
  onDeactivate,
}) {
  const toast = useToast();
  const [modalOpen, setModalOpen] = useState(false);
  const wasSubmitting = useRef(false);
  const pendingModeRef = useRef("create");

  useEffect(() => {
    if (wasSubmitting.current && !formState.submitting && !formState.error) {
      setModalOpen(false);
      if (pendingModeRef.current === "create") {
        toast.success("Usuario creado correctamente.");
      } else {
        toast.success("Usuario actualizado correctamente.");
      }
    }
    wasSubmitting.current = formState.submitting;
  }, [formState.submitting, formState.error]);

  function openCreate() {
    pendingModeRef.current = "create";
    onCancelEdit();
    setModalOpen(true);
  }

  function openEdit(user) {
    pendingModeRef.current = "edit";
    onSelectEdit(user);
    setModalOpen(true);
  }

  async function handleDeactivate(user) {
    const result = await onDeactivate(user);
    if (result === true) {
      toast.success(`${user.first_name} ${user.last_name} desactivado.`);
    } else if (result === false) {
      toast.error("No fue posible desactivar el usuario.");
    }
  }

  function closeModal() {
    setModalOpen(false);
    onCancelEdit();
  }

  const modalTitle =
    formMode === "edit" && selectedUser
      ? `Editar: ${selectedUser.first_name} ${selectedUser.last_name}`
      : "Nuevo usuario";

  return (
    <section className="panel-card dashboard-card users-dashboard-card">
      <header className="page-header">
        <h1 className="page-title">Usuarios</h1>
        <div className="actions-inline">
          <button type="button" onClick={openCreate}>
            + Nuevo usuario
          </button>
          <button className="secondary" type="button" onClick={onRefresh}>
            Recargar
          </button>
        </div>
      </header>

      <div className="users-table-section">
        <UsersTablePanel
          users={users}
          usersLoading={usersLoading}
          usersError={usersError}
          onEdit={openEdit}
          onDeactivate={handleDeactivate}
        />
      </div>

      <Modal open={modalOpen} title={modalTitle} onClose={closeModal}>
        <UserFormPanel
          formMode={formMode}
          formState={formState}
          selectedUser={selectedUser}
          roles={roles}
          onChange={onFormChange}
          onSubmit={onFormSubmit}
          onCancelEdit={closeModal}
        />
      </Modal>
    </section>
  );
}
