async function fetchApplications() {
    try {
      const response = await fetch('/api/users/', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        console.error("Ошибка получения пользователей:", response.status);
        return;
      }

      const data = await response.json();

      const tableBody = document.getElementById("users-table-body");
      tableBody.innerHTML = ""; // очищаем старые данные

      data.forEach(app => {
        const row = document.createElement("tr");

        row.innerHTML = `
          <td>${app.id}</td>
          <td>${app.login}</td>
          <td>${'*'.repeat(8)}</td>
          <td>${app.role}</td>
        `;

        tableBody.appendChild(row);
      });

    } catch (error) {
      console.error("Ошибка сети при получении пользователей:", error);
    }
  }

  document.addEventListener('DOMContentLoaded', fetchApplications);