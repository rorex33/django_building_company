async function fetchApplications() {
    try {
      const response = await fetch('/api/application-types/', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        console.error("Ошибка получения типов заявок:", response.status);
        return;
      }

      const data = await response.json();

      const tableBody = document.getElementById("application-types-table-body");
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
      console.error("Ошибка сети при получении типов заявок:", error);
    }
  }

  document.addEventListener('DOMContentLoaded', fetchApplications);