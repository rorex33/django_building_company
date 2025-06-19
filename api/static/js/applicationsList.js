async function fetchApplications() {
    try {
      const response = await fetch('/api/applications/', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        console.error("Ошибка получения заявок:", response.status);
        return;
      }

      const data = await response.json();

      const tableBody = document.getElementById("application-table-body");
      tableBody.innerHTML = ""; // очищаем старые данные

      data.forEach(app => {
        const row = document.createElement("tr");

        row.innerHTML = `
          <td>${app.id}</td>
          <td>${app.fullName}</td>
          <td>${app.phoneNumber}</td>
          <td>${app.description}</td>
          <td>${app.type.name}</td>
          <td>${app.status.name}</td>
          <td>${new Date(app.date).toLocaleString('ru-RU', {
              day: '2-digit',
              month: '2-digit',
              year: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
          })}</td>
        `;

        tableBody.appendChild(row);
      });

    } catch (error) {
      console.error("Ошибка сети при получении заявок:", error);
    }
  }

  document.addEventListener('DOMContentLoaded', fetchApplications);