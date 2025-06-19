async function fetchApplications() {
    try {
      const response = await fetch('/api/objects/', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        console.error("Ошибка получения объектов:", response.status);
        return;
      }

      const data = await response.json();

      const tableBody = document.getElementById("objects-table-body");
      tableBody.innerHTML = ""; // очищаем старые данные

      data.forEach(app => {
        const row = document.createElement("tr");

        row.innerHTML = `
          <td>${app.id}</td>
          <td>${app.name}</td>
          <td>${app.address}</td>
          <td>${app.description}</td>
        `;

        tableBody.appendChild(row);
      });

    } catch (error) {
      console.error("Ошибка сети при получении объектов:", error);
    }
  }

  document.addEventListener('DOMContentLoaded', fetchApplications);