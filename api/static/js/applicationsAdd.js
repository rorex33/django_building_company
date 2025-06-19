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

document.getElementById("application-form").addEventListener("submit", async function (e) {
    e.preventDefault();

    const fullName = document.getElementById("name").value.trim();
    const phoneNumber = document.getElementById("phoneNumber").value.trim();
    const description = document.getElementById("message").value.trim();

    try {
        const response = await fetch("/api/applications/", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken(),  // Используем уже существующую функцию
        },
        body: JSON.stringify({
            fullName,
            phoneNumber,
            description
        })
        });

        if (response.status === 201) {
        alert("Заявка успешно отправлена!");
        document.getElementById("application-form").reset();
        } else {
        const errorData = await response.json();
        console.error("Ошибка при отправке заявки:", errorData);
        alert("Ошибка при отправке. Проверьте поля.");
        }
    } catch (err) {
        console.error("Ошибка сети:", err);
        alert("Ошибка сети. Попробуйте позже.");
    }
    });