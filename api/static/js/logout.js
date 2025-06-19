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

document.getElementById("logout-btn").addEventListener("click", async function () {
  try {
    const response = await fetch('/api/logout/', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),  // Используем уже существующую функцию
      }
    });

    if (response.ok) {
      // Успешный выход — перенаправляем на страницу логина
      window.location.href = "/pages/auth/";
    } else {
      console.error("Ошибка при выходе:", response.status);
      alert("Не удалось выйти из аккаунта.");
    }
  } catch (error) {
    console.error("Ошибка сети при выходе:", error);
    alert("Ошибка сети. Попробуйте позже.");
  }
});
