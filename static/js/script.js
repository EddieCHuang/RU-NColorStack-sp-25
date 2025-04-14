// Connect to the Flask server via Socket.IO
const socket = io.connect("http://127.0.0.1:5001");

const numberOfRows = 6; // Change this to any number of rows you want
const tableBody = document.querySelector("#myTable tbody");

for (let i = 0; i < numberOfRows; i++) { //for loop to stop at 6th row
  const row = document.createElement("tr");
  for (let j = 0; j < 5; j++) {
    const cell = document.createElement("td");
    cell.textContent = `R${i + 1}C${j + 1}`;
    row.appendChild(cell);
  }
  tableBody.appendChild(row);
}


// When system info is received from the server
socket.on('system_info', function(data) {
    console.log("📡 Received system_info:", data);
  // Clear existing table rows
  const tableBody = document.querySelector("#myTable tbody");
  // Clear the table
  tableBody.innerHTML = "";

  try {
    // Extract the data (modify based on your actual structure)
    const cpuUsage = data["CPU Info"]["Total CPU Usage"];
    const memoryUsage = data["Memory Info"]["Percentage"];
    const diskUsage = data["Disk Info"]["sda1"]["Percentage"];
    const temperature = data["GPU Info"]["GPU_0"]["Temperature"];
    const uptime = data["System Info"]["Uptime"];

    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${cpuUsage}</td>
      <td>${memoryUsage}</td>
      <td>${diskUsage}</td>
      <td>${temperature}</td>
      <td>${uptime}</td>
    `;

    tableBody.appendChild(row);
  } catch (error) {
    console.error("❌ Error building table row from data:", error);
  }
});

