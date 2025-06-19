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
    change: document.getElementById('clientsApplicationsChangeForm'),
    delete: document.getElementById('clientsApplicationsDeleteForm'),
    error: document.getElementById('clientsApplicationsErrorModal'),
    success: document.getElementById('clientsApplicationsSuccessModal')
  };

  // Кнопки
  const buttons = {
    edit: document.getElementById('btnOpenEdit'),
    delete: document.getElementById('deleteSubmitBtn'),
    changeSubmit: document.querySelector('#clientsApplicationsChangeForm button[type="submit"]'),
    confirmDelete: document.getElementById('confirmDeleteBtn')
  };

  // Таблица
  const table = {
    // Находим таблицу по id
    body: document.getElementById('application-table-body'),
    // Определяем, какие у неё есть ячейки
    cells: {
      id: document.getElementById('id'),
      fullName: document.getElementById('fullName'),
      phoneNumber: document.getElementById('phoneNumber'),
      description: document.getElementById('description'),
      type: document.getElementById('typeId'),
      status: document.getElementById('statusId')
    },
    // Какие элементы таблицы показываем при удалении
    deleteInfo: {
      name: document.getElementById('deleteAppName'),
      phone: document.getElementById('deleteAppPhone'),
      type: document.getElementById('deleteAppType')
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
      const response = await fetch('/api/applications/', {
        credentials: 'include'
      });
      if (!response.ok) throw new Error();
      return await response.json();
    } catch (error) {
      console.error('Ошибка загрузки заявок:', error);
      modals.error.classList.remove('hidden');
      return [];
    }
  }

  async function updateTable() {
    const applications = await fetchApplications();
    table.body.innerHTML = applications.map(app => `
      <tr>
        <td>${app.id}</td>
        <td>${app.fullName}</td>
        <td>${app.phoneNumber}</td>
        <td>${app.description}</td>
        <td>${app.type?.name || ''}</td>
        <td>${app.status?.name || ''}</td>
        <td>${new Date(app.date).toLocaleDateString()}</td>
      </tr>
    `).join('');
  }

  async function populateSelectOptions() {
    try {
      const [typesRes, statusesRes] = await Promise.all([
        fetch('/api/application-types/'),
        fetch('/api/application-statuses/')
      ]);
      if (!typesRes.ok || !statusesRes.ok) throw new Error();

      const [types, statuses] = await Promise.all([
        typesRes.json(),
        statusesRes.json()
      ]);

      const updateSelect = (select, items) => {
        select.innerHTML = '<option value="" disabled selected hidden>' + 
                          select.getAttribute('placeholder') + '</option>';
        items.forEach(item => {
          const option = document.createElement('option');
          option.value = item.name;
          option.textContent = item.name;
          select.appendChild(option);
        });
      };

      updateSelect(table.cells.type, types);
      updateSelect(table.cells.status, statuses);
    } catch (error) {
      console.error('Ошибка загрузки данных:', error);
      modals.error.classList.remove('hidden');
    }
  }

  // Обработчики событий
  
  // Клик на строку
  table.body.addEventListener('click', (event) => {
    const row = event.target.closest('tr');
    if (!row) return;

    // Снимаем выделение со всех строк
    document.querySelectorAll('#application-table-body tr').forEach(r => 
      r.classList.remove('selected'));
    
    // Выделяем текущую строку
    row.classList.add('selected');

    // Сохраняем выбранную заявку
    selectedApplication = {
      id: row.cells[0].textContent.trim(),
      fullName: row.cells[1].textContent.trim(),
      phoneNumber: row.cells[2].textContent.trim(),
      description: row.cells[3].textContent.trim(),
      type: { name: row.cells[4].textContent.trim() },
      status: { name: row.cells[5].textContent.trim() }
    };
  });

  buttons.edit.addEventListener('click', () => {
    if (!selectedApplication) {
      alert('Пожалуйста, выберите заявку из списка');
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
      alert('Пожалуйста, выберите заявку из списка');
      return;
    }

    // Заполняем информацию о заявке в модальном окне
    table.deleteInfo.name.textContent = selectedApplication.fullName;
    table.deleteInfo.phone.textContent = selectedApplication.phoneNumber;
    table.deleteInfo.type.textContent = selectedApplication.type.name;

    modals.delete.classList.remove('hidden');
  });

  buttons.changeSubmit.addEventListener('click', async (e) => {
    e.preventDefault();

    const data = {
      fullName: table.cells.fullName.value,
      phoneNumber: table.cells.phoneNumber.value,
      description: table.cells.description.value,
      type_name: table.cells.type.value,
      status_name: table.cells.status.value
    };

    try {
      const response = await fetch(`/api/applications/${selectedApplication.id}/`, {
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
      const response = await fetch(`/api/applications/${selectedApplication.id}/`, {
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
    await populateSelectOptions();
    await updateTable();
  }

  init();
});