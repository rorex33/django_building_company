// Функция для получения CSRF токена
function getCsrfToken() {
  const name = 'csrftoken';
  const cookies = document.cookie.split(';');

  for (let i = 0; i < cookies.length; i++) {
    const cookie = cookies[i].trim();
    if (cookie.startsWith(name + '=')) {
      return decodeURIComponent(cookie.substring(name.length + 1));
    }
  }
  console.error("CSRF токен не найден в cookies!");
  return null;
}

document.addEventListener('DOMContentLoaded', () => {
  // Элементы DOM

  // Формы
  const modals = {
    add: document.getElementById('clientsApplicationsTypesAddForm'),
    change: document.getElementById('clientsApplicationsTypesChangeForm'),
    delete: document.getElementById('clientsApplicationsTypesDeleteForm'),
    error: document.getElementById('clientsApplicationsTypesErrorModal'),
    success: document.getElementById('clientsApplicationsTypesSuccessModal')
  };

  // Кнопки
  const buttons = {
    add: document.getElementById('btnAdd'),
    edit: document.getElementById('btnOpenEdit'),
    delete: document.getElementById('deleteSubmitBtn'),
    addSubmit: document.querySelector('#clientsApplicationsTypesAddForm button[type="submit"]'),
    changeSubmit: document.querySelector('#clientsApplicationsTypesChangeForm button[type="submit"]'),
    confirmDelete: document.getElementById('confirmDeleteBtn')
  };

  // Таблица
  const table = {
    // Находим таблицу по id
    body: document.getElementById('application-types-table-body'),
    // Определяем, какие у неё есть ячейки
    cells: {
      id: document.getElementById('id'),
      name: document.getElementById('editName'),
      description: document.getElementById('editDescription'),
    },
    // Какие элементы таблицы показываем при удалении
    deleteInfo: {
      name: document.getElementById('deleteTypeName'),
    },
    // Какие поля нужно добавлять в таблицу (id не указываем)
    addFields: {
      name: document.getElementById('addName'),
      description: document.getElementById('addDescription')
    }
  };

  let selectedApplication = null;

  // Функции
  function closeAllModals() {
    Object.values(modals).forEach(modal => modal.classList.add('hidden'));
  }
  window.closeModal = closeAllModals;

  async function fetchApplications() {
    try {
      const response = await fetch('/api/application-types/', {
        credentials: 'include'
      });
      if (!response.ok) throw new Error();
      return await response.json();
    } catch (error) {
      console.error('Ошибка загрузки типов заявок:', error);
      modals.error.classList.remove('hidden');
      return [];
    }
  }

  async function updateTable() {
    const applications = await fetchApplications();
    table.body.innerHTML = applications.map(app => `
      <tr>
        <td>${app.id}</td>
        <td>${app.name}</td>
        <td>${app.description}</td>
      </tr>
    `).join('');
  }

  // Обработчики событий

  // Клик на строку
  table.body.addEventListener('click', (event) => {
    const row = event.target.closest('tr');
    if (!row) return;

    // Снимаем выделение со всех строк
    document.querySelectorAll('#application-types-table-body tr').forEach(r => 
      r.classList.remove('selected'));
    
    // Выделяем текущую строку
    row.classList.add('selected');

    // Сохраняем выбранную заявку
    selectedApplication = {
      id: row.cells[0].textContent.trim(),
      name: row.cells[1].textContent.trim(),
      description: row.cells[2].textContent.trim(),
    };
  });

  // Обработчик кнопки добавления
  buttons.add.addEventListener('click', () => {
    modals.add.classList.remove('hidden');
  });

  // Обработчик отправки формы добавления
  buttons.addSubmit.addEventListener('click', async (e) => {
    e.preventDefault();

    const data = {
      name: table.addFields.name.value.trim(),
      description: table.addFields.description.value.trim()
    };

    try {
      const response = await fetch('/api/application-types/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken()
        },
        credentials: 'include',
        body: JSON.stringify(data)
      });

      if (response.status === 201) {
        closeAllModals();
        modals.success.classList.remove('hidden');
        table.addFields.name.value = '';
        table.addFields.description.value = '';
        await updateTable();
      } else {
        const errorData = await response.json();
        console.error("Ошибка при добавлении:", errorData);
        modals.error.classList.remove('hidden');
      }
    } catch (err) {
      console.error("Ошибка сети:", err);
      modals.error.classList.remove('hidden');
    }
  });

  buttons.edit.addEventListener('click', () => {
    if (!selectedApplication) {
      alert('Пожалуйста, выберите тип заявок из списка');
      return;
    }

    // Заполняем форму данными
    Object.entries(selectedApplication).forEach(([key, value]) => {
      if (table.cells[key]) {
        table.cells[key].value = typeof value === 'object' ? value.name : value;
      }
    });

    modals.change.classList.remove('hidden');
  });

  buttons.delete.addEventListener('click', () => {
    if (!selectedApplication) {
      alert('Пожалуйста, выберите тип заявок из списка');
      return;
    }

    // Что показать при удалении
    table.deleteInfo.name.textContent = selectedApplication.name;
    
    modals.delete.classList.remove('hidden');
  });

  buttons.changeSubmit.addEventListener('click', async (e) => {
    e.preventDefault();

    const data = {
      name: table.cells.name.value,
      description: table.cells.description.value,
    };

    try {
      const response = await fetch(`/api/application-types/${selectedApplication.id}/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken()
        },
        credentials: 'include',
        body: JSON.stringify(data)
      });

      if (!response.ok) throw new Error();

      closeAllModals();
      modals.success.classList.remove('hidden');
      await updateTable();
    } catch (error) {
      console.error('Ошибка при изменении:', error);
      closeAllModals();
      modals.error.classList.remove('hidden');
    }
  });

  buttons.confirmDelete.addEventListener('click', async () => {
    try {
      const response = await fetch(`/api/application-types/${selectedApplication.id}/`, {
        method: 'DELETE',
        headers: {
          'X-CSRFToken': getCsrfToken()
        },
        credentials: 'include'
      });

      if (!response.ok) throw new Error();

      closeAllModals();
      modals.success.classList.remove('hidden');
      await updateTable();
    } catch (error) {
      console.error('Ошибка при удалении:', error);
      closeAllModals();
      modals.error.classList.remove('hidden');
    }
  });

  // Инициализация
  async function init() {
    await updateTable();
  }

  init();
});