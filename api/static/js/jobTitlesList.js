async function fetchApplications() {
    try {
      const response = await fetch('/api/job-titles/', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        console.error("Ошибка получения должностей:", response.status);
        return;
      }

      const data = await response.json();

      const tableBody = document.getElementById("jobTitles-table-body");
      tableBody.innerHTML = ""; // очищаем старые данные

      data.forEach(app => {
        const row = document.createElement("tr");

        row.innerHTML = `
          <td>${app.id}</td>
          <td>${app.name}</td>
        `;

        tableBody.appendChild(row);
      });

    } catch (error) {
      console.error("Ошибка сети при получении должностей:", error);
    }
  }

  document.addEventListener('DOMContentLoaded', fetchApplications);