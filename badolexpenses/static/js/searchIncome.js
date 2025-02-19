const searchField = document.querySelector("#searchField");

const tableOutput = document.querySelector(".table-output");
const appTable = document.querySelector(".app-table");
const paginationContainer = document.querySelector(".pagination-container");
tableOutput.style.display = "none";
const noResults = document.querySelector(".no-results");
const tbody = document.querySelector(".table-body");

searchField.addEventListener("keyup", (e) => {
  const searchValue = e.target.value;

  if (searchValue.trim().length > 0) {
    paginationContainer.style.display = "none";
    tbody.innerHTML = "";
    fetch("/income/search-income", {
      body: JSON.stringify({ searchText: searchValue }),
      method: "POST",
    })
      .then((res) => res.json())
      .then((data) => {
        console.log("data", data);
        appTable.style.display = "none";
        tableOutput.style.display = "block";

        if (data.length === 0) {
          noResults.style.display = "block";
          tableOutput.style.display = "none";
        } else {
          noResults.style.display = "none";
          data.forEach((item) => {
            tbody.innerHTML += `
                <tr>
                <td>${item.amount}</td>
                <td>${item.source}</td>
                <td>${item.categories}</td>
                <td>${item.versements}</td>
                <td>${item.description}</td>
                <td>${item.date}</td>
                <td><a href="/income/edit-income/${item.id}" class="btn btn-outline-success btn-sm" style="border-radius: 12px;"
                >Editer</a></td>
                <td>
                  <span onclick="reply_click(this.id)"  id="${item.id}" style="cursor: pointer;">
                  <p onclick="document.getElementById('id01').style.display='block'" class="btn btn-outline-success btn-sm" style="border-radius: 12px;"
                  >Supprimer</p>
                  </span>
                  </td>
                </tr>`;
          });
        }
      });
  } else {
    tableOutput.style.display = "none";
    appTable.style.display = "block";
    paginationContainer.style.display = "block";
  }
});
