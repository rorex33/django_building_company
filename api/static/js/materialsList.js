async function fetchApplications() {
    try {
      const response = await fetch('/api/materials/', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        console.error("Ошибка получения материалов:", response.status);
        return;
      }

      const data = await response.json();

      const tableBody = document.getElementById("materials-table-body");
      tableBody.innerHTML = ""; // очищаем старые данные

      data.forEach(app => {
        const row = document.createElement("tr");

        row.innerHTML = `
          <td>${app.id}</td>
          <td>${app.name}</td>
          <td>${app.amount}</td>
          <td>${app.object}</td>
        `;

        tableBody.appendChild(row);
      });

    } catch (error) {
      console.error("Ошибка сети при получении материалов:", error);
    }
  }

  document.addEventListener('DOMContentLoaded', fetchApplications);