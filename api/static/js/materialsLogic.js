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
    add: document.getElementById('materialsAddForm'),
    change: document.getElementById('materialsChangeForm'),
    delete: document.getElementById('materialsDeleteForm'),
    error: document.getElementById('materialsErrorModal'),
    success: document.getElementById('materialsSuccessModal')
  };

  // Кнопки
  const buttons = {
    add: document.getElementById('btnAdd'),
    edit: document.getElementById('btnOpenEdit'),
    delete: document.getElementById('deleteSubmitBtn'),
    addSubmit: document.querySelector('#materialsAddForm button[type="submit"]'),
    changeSubmit: document.querySelector('#materialsChangeForm button[type="submit"]'),
    confirmDelete: document.getElementById('confirmDeleteBtn')
  };

  // Таблица
  const table = {
    // Находим таблицу по id
    body: document.getElementById('materials-table-body'),
    // Определяем, какие у неё есть ячейки
    cells: {
      id: document.getElementById('id'),
      name: document.getElementById('editName'),
      amount: document.getElementById('editAmount'),
      objects: document.getElementById('editObjectId'),
    },
    // Какие элементы таблицы показываем при удалении
    deleteInfo: {
      name: document.getElementById('deleteMaterialName'),
      amount: document.getElementById('deleteMaterialAmount'),
    },
    // Какие поля нужно добавлять в таблицу (id не указываем)
    addFields: {
      name: document.getElementById('addName'),
      amount: document.getElementById('addAmount'),
      object: document.getElementById('addObjectId'),
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
      const response = await fetch('/api/materials/', {
        credentials: 'include'
      });
      if (!response.ok) throw new Error();
      return await response.json();
    } catch (error) {
      console.error('Ошибка загрузки материалов:', error);
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
          <td>${app.amount}</td>
          <td>${app.object}</td>
      </tr>
    `).join('');
  }

  async function populateSelectOptions() {
    try {
        const objectRes = await fetch('/api/objects/');
        if (!objectRes.ok) throw new Error();

        const objects = await objectRes.json();

        const updateSelect = (select, items) => {
        if (!select) return;
        select.innerHTML = '<option value="" disabled selected hidden>Объект использования</option>';
        items.forEach(item => {
            const option = document.createElement('option');
            option.value = item.name;
            option.textContent = item.name;
            select.appendChild(option);
        });
        };

        updateSelect(table.cells.objects, objects);              // форма изменения
        updateSelect(table.addFields.object, objects);           // форма добавления

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
    document.querySelectorAll('#materials-table-body tr').forEach(r => 
      r.classList.remove('selected'));
    
    // Выделяем текущую строку
    row.classList.add('selected');

    // Сохраняем выбранную заявку
    selectedApplication = {
      id: row.cells[0].textContent.trim(),
      name: row.cells[1].textContent.trim(),
      amount: row.cells[2].textContent.trim(),
      objects: { name: row.cells[3].textContent.trim() }
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
      amount: table.addFields.amount.value.trim(),
      object: table.addFields.object.value.trim()
    };

    try {
      const response = await fetch('/api/materials/', {
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
      alert('Пожалуйста, выберите материал из списка');
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
      alert('Пожалуйста, выберите материал из списка');
      return;
    }

    // Что показать при удалении
    table.deleteInfo.name.textContent = selectedApplication.name;
    table.deleteInfo.amount.textContent = selectedApplication.amount;
    
    modals.delete.classList.remove('hidden');
  });

  buttons.changeSubmit.addEventListener('click', async (e) => {
    e.preventDefault();

    const data = {
      name: table.cells.name.value,
      amount: table.cells.amount.value,
    };

    try {
      const response = await fetch(`/api/materials/${selectedApplication.id}/`, {
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
      const response = await fetch(`/api/materials/${selectedApplication.id}/`, {
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