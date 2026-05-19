import { useEffect, useMemo, useState } from "react";

import {
  createUser,
  deactivateUser,
  fetchRoles,
  fetchUsers,
  updateUser,
} from "../services/usersApi";

export function useUsersManagement({ authToken, enabled }) {
  const [roles, setRoles] = useState([]);
  const [users, setUsers] = useState([]);
  const [usersLoading, setUsersLoading] = useState(false);
  const [usersError, setUsersError] = useState("");
  const [formMode, setFormMode] = useState("create");
  const [selectedUserId, setSelectedUserId] = useState(null);
  const [formState, setFormState] = useState({
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    role_id: "",
    is_active: true,
    submitting: false,
    error: "",
  });

  const selectedUser = useMemo(
    () => users.find((user) => user.id === selectedUserId) ?? null,
    [users, selectedUserId],
  );

  const resetFormToCreate = () => {
    setFormMode("create");
    setSelectedUserId(null);
    setFormState((previous) => ({
      ...previous,
      email: "",
      password: "",
      first_name: "",
      last_name: "",
      role_id: roles[0] ? String(roles[0].id) : "",
      is_active: true,
      submitting: false,
      error: "",
    }));
  };

  const loadUsersAndRoles = async () => {
    if (!authToken) {
      return;
    }

    setUsersLoading(true);
    setUsersError("");

    try {
      const [fetchedRoles, fetchedUsers] = await Promise.all([
        fetchRoles(authToken),
        fetchUsers(authToken),
      ]);
      setRoles(fetchedRoles);
      setUsers(fetchedUsers);

      setFormState((previous) => {
        if (previous.role_id || fetchedRoles.length === 0) {
          return previous;
        }

        return {
          ...previous,
          role_id: String(fetchedRoles[0].id),
        };
      });
    } catch (error) {
      setUsersError(error.message || "No fue posible cargar usuarios y roles.");
    } finally {
      setUsersLoading(false);
    }
  };

  useEffect(() => {
    if (!enabled) {
      return;
    }

    loadUsersAndRoles();
  }, [authToken, enabled]);

  const handleSelectEdit = (user) => {
    setFormMode("edit");
    setSelectedUserId(user.id);
    setFormState((previous) => ({
      ...previous,
      email: user.email,
      password: "",
      first_name: user.first_name,
      last_name: user.last_name,
      role_id: String(user.role.id),
      is_active: user.is_active,
      error: "",
    }));
  };

  const handleSubmitForm = async (event) => {
    event.preventDefault();
    setFormState((previous) => ({ ...previous, submitting: true, error: "" }));

    const payload = {
      email: formState.email,
      first_name: formState.first_name,
      last_name: formState.last_name,
      role_id: Number(formState.role_id),
      is_active: formState.is_active,
    };

    if (formMode === "create") {
      payload.password = formState.password;
    }

    try {
      if (formMode === "create") {
        await createUser(authToken, payload);
      } else {
        await updateUser(authToken, selectedUserId, payload);
      }

      await loadUsersAndRoles();
      resetFormToCreate();
    } catch (error) {
      setFormState((previous) => ({
        ...previous,
        submitting: false,
        error: error.message || "No se pudo guardar el usuario.",
      }));
      return;
    }

    setFormState((previous) => ({ ...previous, submitting: false }));
  };

  const handleDeactivateUser = async (user) => {
    const approved = window.confirm(`Desactivar a ${user.first_name} ${user.last_name}?`);
    if (!approved) {
      return;
    }

    try {
      await deactivateUser(authToken, user.id);
      await loadUsersAndRoles();

      if (selectedUserId === user.id) {
        resetFormToCreate();
      }
    } catch (error) {
      setUsersError(error.message || "No se pudo desactivar el usuario.");
    }
  };

  return {
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
  };
}
