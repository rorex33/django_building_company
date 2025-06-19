async function fetchApplications() {
    try {
      const response = await fetch('/api/application-statuses/', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        console.error("Ошибка получения статусов заявок:", response.status);
        return;
      }

      const data = await response.json();

      const tableBody = document.getElementById("application-statuses-table-body");
      tableBody.innerHTML = ""; // очищаем старые данные

      data.forEach(app => {
        const row = document.createElement("tr");

        row.innerHTML = `
          <td>${app.id}</td>
          <td>${app.name}</td>
          <td>${app.description}</td>
        `;

        tableBody.appendChild(row);
      });

    } catch (error) {
      console.error("Ошибка сети при получении статусов заявок:", error);
    }
  }

  document.addEventListener('DOMContentLoaded', fetchApplications);