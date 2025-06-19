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

// Проверка статуса аутентификации при загрузке страницы
async function checkAuthStatus() {
  try {
    const response = await fetch('/api/check-login/', {
      method: 'GET',
      credentials: 'include',
    });
    
    if (response.status === 403) {
      // Пользователь не аутентифицирован - остаемся на странице входа
      return;
    }
    
    if (response.ok) {
      const data = await response.json();
      if (data.logged_in) {
        // Если пользователь уже вошел - перенаправляем на dashboard
        window.location.href = "/pages/dashboard/";
        return;
      }
    }
    
    // Если ответ не 403, но и не OK - возможно, проблема с сервером
    console.error('Неожиданный ответ сервера:', response.status);
  } catch (error) {
    console.error('Ошибка при проверке статуса входа:', error);
  }
}

// Обработчик формы входа
document.getElementById("login-form").addEventListener("submit", async function(e) {
  e.preventDefault();
  const login = document.getElementById("login").value.trim();
  const password = document.getElementById("password").value.trim();

  try {
    const response = await fetch('/api/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      credentials: 'include',
      body: JSON.stringify({ login, password })
    });

    const result = await response.json();

    if (result.status === 'Success') {
      window.location.href = "/pages/dashboard/";
    } else {
      showError(result.error || "Ошибка при входе");
    }
  } catch (error) {
    showError("Ошибка сети. Пожалуйста, попробуйте позже.");
    console.error('Ошибка при входе:', error);
  }
});

// Функция показа ошибки
function showError(message) {
  const errorModal = document.getElementById("error-modal");
  const errorText = errorModal.querySelector(".modalBox p"); // находим <p> с текстом ошибки
  errorText.textContent = message;  // меняем текст ошибки
  errorModal.classList.remove("hidden"); // показываем модалку
}

// Функция закрытия модального окна
function closeModal() {
  document.getElementById("error-modal").classList.add("hidden");
}

// Проверяем статус аутентификации при загрузке страницы
document.addEventListener('DOMContentLoaded', checkAuthStatus);