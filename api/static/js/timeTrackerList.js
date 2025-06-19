async function fetchApplications() {
    try {
      const response = await fetch('/api/wtt/listWTT/', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        console.error("Ошибка получения учёта времени:", response.status);
        return;
      }

      const data = await response.json();

      const tableBody = document.getElementById("timeTracker-table-body");
      tableBody.innerHTML = ""; // очищаем старые данные

      data.forEach(app => {
        const row = document.createElement("tr");

        row.innerHTML = `
          <td>${app.id}</td>
          <td>${app.employee.personnelNumber}</td>
          <td>${app.date}</td>
          <td>${app.startTime.slice(0,8)}</td>
          <td>${app.endTime.slice(0,8)}</td>
        `;

        tableBody.appendChild(row);
      });

    } catch (error) {
      console.error("Ошибка сети при получении учёта времени:", error);
    }
  }

  document.addEventListener('DOMContentLoaded', fetchApplications);