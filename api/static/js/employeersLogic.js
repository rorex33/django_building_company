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
    add: document.getElementById('employeersAddForm'),
    change: document.getElementById('employeersChangeForm'),
    delete: document.getElementById('employeersDeleteForm'),
    error: document.getElementById('employeersErrorModal'),
    success: document.getElementById('employeersSuccessModal')
  };

  // Кнопки
  const buttons = {
    add: document.getElementById('btnAdd'),
    edit: document.getElementById('btnOpenEdit'),
    delete: document.getElementById('deleteSubmitBtn'),
    addSubmit: document.querySelector('#employeersAddForm button[type="submit"]'),
    changeSubmit: document.querySelector('#employeersChangeForm button[type="submit"]'),
    confirmDelete: document.getElementById('confirmDeleteBtn')
  };

  // Таблица
  const table = {
    // Находим таблицу по id
    body: document.getElementById('employeers-table-body'),
    // Определяем, какие у неё есть ячейки
    cells: {
      id: document.getElementById('id'),
      fullName: document.getElementById('editFullName'),
      personnelNumber: document.getElementById('editPersonnelNumber'),
      phoneNumber: document.getElementById('editPhoneNumber'),
      email: document.getElementById('editEmail'),
      bankDetails: document.getElementById('editBankDetails'),
      passport: document.getElementById('editPassport'),
      jobTitles: document.getElementById('editJobTitleId'),
      objects: document.getElementById('editObjectId'),
      users: document.getElementById('editUserId'),
    },
    // Какие элементы таблицы показываем при удалении
    deleteInfo: {
      fullName: document.getElementById('deletEemployeerFullName'),
      personnelNumber: document.getElementById('deletEemployeerPersonnelNumber'),
      phoneNumber: document.getElementById('deletEemployeerPhoneNumber'),
    },
    // Какие поля нужно добавлять в таблицу (id не указываем)
    addFields: {
      id: document.getElementById('id'),
      fullName: document.getElementById('addFullName'),
      personnelNumber: document.getElementById('addPersonnelNumber'),
      phoneNumber: document.getElementById('addPhoneNumber'),
      email: document.getElementById('addEmail'),
      bankDetails: document.getElementById('addBankDetails'),
      passport: document.getElementById('addPassport'),
      jobTitle: document.getElementById('addJobTitleId'),
      object: document.getElementById('addObjectId'),
      user: document.getElementById('addUserId'),
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
      const response = await fetch('/api/employees/', {
        credentials: 'include'
      });
      if (!response.ok) throw new Error();
      return await response.json();
    } catch (error) {
      console.error('Ошибка загрузки сотрудников:', error);
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
          <td>${app.personnelNumber}</td>
          <td>${app.phoneNumber}</td>
          <td>${app.email}</td>\
          <td>${app.bankDetails}</td>
          <td>${app.passport}</td>
          <td>${app.jobTitle}</td>
          <td>${app.object}</td>
          <td>${app.user}</td>
      </tr>
    `).join('');
  }

async function populateSelectOptions() {
  try {
    // 1. Получаем должности
    const jobsRes = await fetch('/api/job-titles/');
    if (!jobsRes.ok) throw new Error('Ошибка загрузки объектов');
    const jobs = await jobsRes.json();

    // 2. Получаем объекты
    const objectRes = await fetch('/api/objects/');
    if (!objectRes.ok) throw new Error('Ошибка загрузки должностей');
    const objects = await objectRes.json();

    // 3. Получаем пользователей
    const usersRes = await fetch('/api/users/');
    if (!usersRes.ok) throw new Error('Ошибка загрузки пользователей');
    const users = await usersRes.json();

    // Функция для обновления select'ов
    const updateSelect = (select, items, placeholder = 'Выберите...') => {
      if (!select) return;
      select.innerHTML = `<option value="" disabled selected hidden>${placeholder}</option>`;
      items.forEach(item => {
        const option = document.createElement('option');
        option.value = item.name || item.login || item.id;
        option.textContent = item.name || item.login || item.id;
        select.appendChild(option);
      });
    };

    // Заполнение селекторов
    updateSelect(table.addFields.jobTitle, jobs, 'Должность');
    updateSelect(table.addFields.object, objects, 'Объект');
    updateSelect(table.addFields.user, users, 'Пользователь');

    updateSelect(table.cells.jobTitles, jobs, 'Должность');
    updateSelect(table.cells.objects, objects, 'Объект');        // для формы редактирования
    updateSelect(table.cells.users, users, 'Пользователь');

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
    document.querySelectorAll('#employeers-table-body tr').forEach(r => 
      r.classList.remove('selected'));
    
    // Выделяем текущую строку
    row.classList.add('selected');

    // Сохраняем выбранную заявку
    selectedApplication = {
      id: row.cells[0].textContent.trim(),
      fullName: row.cells[1].textContent.trim(),
      personnelNumber: row.cells[2].textContent.trim(),
      phoneNumber: row.cells[3].textContent.trim(),
      email: row.cells[4].textContent.trim(),
      bankDetails: row.cells[5].textContent.trim(),
      passport: row.cells[6].textContent.trim(),
      jobTitles: { name: row.cells[7].textContent.trim() },
      objects: { name: row.cells[8].textContent.trim() },
      users: { name: row.cells[9].textContent.trim() }
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
      fullName: table.addFields.fullName.value.trim(),
      personnelNumber: table.addFields.personnelNumber.value.trim(),
      phoneNumber: table.addFields.phoneNumber.value.trim(),
      email: table.addFields.email.value.trim(),
      bankDetails: table.addFields.bankDetails.value.trim(),
      passport: table.addFields.passport.value.trim(),
      jobTitle: table.addFields.jobTitle.value.trim(),
      object: table.addFields.object.value.trim(),
      user: table.addFields.user.value.trim()
    };

    try {
      const response = await fetch('/api/employees/', {
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
        table.addFields.fullName.value = '';
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
      alert('Пожалуйста, выберите сотурдника из списка');
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
      alert('Пожалуйста, выберите сотурдника из списка');
      return;
    }

    // Что показать при удалении
    table.deleteInfo.fullName.textContent = selectedApplication.fullName;
    table.deleteInfo.personnelNumber.textContent = selectedApplication.personnelNumber;
    table.deleteInfo.phoneNumber.textContent = selectedApplication.phoneNumber;
    
    modals.delete.classList.remove('hidden');
  });

  buttons.changeSubmit.addEventListener('click', async (e) => {
    e.preventDefault();

    const data = {
      fullName: table.cells.fullName.value,
      personnelNumber: table.cells.personnelNumber.value,
      phoneNumber: table.cells.phoneNumber.value,
      email: table.cells.email.value,
      bankDetails: table.cells.bankDetails.value,
      passport: table.cells.passport.value,
      jobTitle: table.cells.jobTitles.value,
      object: table.cells.objects.value.trim,
      user: table.cells.users.value
    };

    try {
      const response = await fetch(`/api/employees/${selectedApplication.id}/`, {
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
      const response = await fetch(`/api/employees/${selectedApplication.id}/`, {
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