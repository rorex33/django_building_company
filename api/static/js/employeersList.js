async function fetchApplications() {
    try {
      const response = await fetch('/api/employees/', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        console.error("Ошибка получения сотрудников:", response.status);
        return;
      }

      const data = await response.json();

      const tableBody = document.getElementById("employeers-table-body");
      tableBody.innerHTML = ""; // очищаем старые данные

      data.forEach(app => {
        const row = document.createElement("tr");

        row.innerHTML = `
          <td>${app.id}</td>
          <td>${app.fullName}</td>
          <td>${app.personnelNumber}</td>
          <td>${app.phoneNumber}</td>
          <td>${app.email}</td>\
          <td>${app.bankDetails}</td>
          <td>${app.passport}</td>
          <td>${app.jobTitle}</td>
          <td>${app.object}</td>
          <td>${app.user}</td>
        `;

        tableBody.appendChild(row);
      });

    } catch (error) {
      console.error("Ошибка сети при получении сотрудников:", error);
    }
  }

  document.addEventListener('DOMContentLoaded', fetchApplications);