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
    change: document.getElementById('timeTrackerChangeForm'),
    error: document.getElementById('timeTrackerErrorModal'),
    success: document.getElementById('timeTrackerSuccessModal'),
  };

  // Кнопки
  const buttons = {
    startDay: document.getElementById('startBtn'),
    endDay: document.getElementById('endBtn'),
    change: document.getElementById('btnOpenEdit'),
    changeSubmit: document.querySelector('#timeTrackerChangeForm button[type="submit"]'),
  };

  // Таблица
  const table = {
    // Находим таблицу по id
    body: document.getElementById('timeTracker-table-body'),
    // Определяем, какие у неё есть ячейки
    cells: {
      id: document.getElementById('id'),
      employees: document.getElementById('employeeId'),
      date: document.getElementById('date'),
      startTime: document.getElementById('startTime'),
      endTime: document.getElementById('endTime'),
    },
  };

  let selectedApplication = null;

  // Функции
  function closeAllModals() {
    Object.values(modals).forEach(modal => modal.classList.add('hidden'));
  }
  window.closeModal = closeAllModals;

  async function fetchApplications() {
    try {
      const response = await fetch('/api/wtt/listWTT/', {
        credentials: 'include'
      });
      if (!response.ok) throw new Error();
      return await response.json();
    } catch (error) {
      console.error('Ошибка загрузки учёта времени:', error);
      modals.error.classList.remove('hidden');
      return [];
    }
  }

  async function updateTable() {
    const applications = await fetchApplications();
    table.body.innerHTML = applications.map(app => `
      <tr>
         <td>${app.id}</td>
          <td>${app.employee.personnelNumber}</td>
          <td>${app.date}</td>
          <td>${app.startTime.slice(0,8)}</td>
          <td>${app.endTime.slice(0,8)}</td>
      </tr>
    `).join('');
  }

  // Обработчики событий

  // Клик на строку
  table.body.addEventListener('click', (event) => {
    const row = event.target.closest('tr');
    if (!row) return;

    // Снимаем выделение со всех строк
    document.querySelectorAll('#timeTracker-table-body tr').forEach(r => 
      r.classList.remove('selected'));
    
    // Выделяем текущую строку
    row.classList.add('selected');

    // Сохраняем выбранную заявку
    selectedApplication = {
      id: row.cells[0].textContent.trim(),
      employees: { name: row.cells[1].textContent.trim() },
      date: row.cells[2].textContent.trim(),
      startTime: row.cells[3].textContent.trim(),
      endTime: row.cells[4].textContent.trim(),
    };
  });

  async function sendStartDay(personnelNumber) {
    try {
      const res = await fetch('/api/wtt/start/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken()
        },
        credentials: 'include',
        body: JSON.stringify({ personnelNumber })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Ошибка старта дня');
      modals.success.classList.remove('hidden');
      await updateTable();
    } catch (err) {
      console.error(err);
      modals.error.classList.remove('hidden');
    }
  }

  async function sendEndDay(personnelNumber) {
    try {
      const res = await fetch('/api/wtt/stop/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken()
        },
        credentials: 'include',
        body: JSON.stringify({ personnelNumber })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Ошибка завершения дня');
      modals.success.classList.remove('hidden');
      await updateTable();
    } catch (err) {
      console.error(err);
      modals.error.classList.remove('hidden');
    }
  }

  // Обработчик cтарта дня
  buttons.startDay.addEventListener('click', () => {
    const personnelNumber = prompt('Введите табельный номер сотрудника:');
    if (personnelNumber) sendStartDay(personnelNumber.trim());
  });

  buttons.endDay.addEventListener('click', () => {
    const personnelNumber = prompt('Введите табельный номер сотрудника:');
    if (personnelNumber) sendEndDay(personnelNumber.trim());
  });

  buttons.change.addEventListener('click', () => {
    if (!selectedApplication) {
      alert('Пожалуйста, выберите временную метку из списка');
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

  buttons.changeSubmit.addEventListener('click', async (e) => {
    e.preventDefault();

    const data = {
      personnelNumber: table.cells.employees.value,
      //date: table.cells.date.value,
      startTime: table.cells.startTime.value,
      endTime: table.cells.endTime.value,
    };

    try {
      const response = await fetch(`/api/wtt/updateWTT/`, {
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

  // Инициализация
  async function init() {
    await updateTable();
  }

  init();
});