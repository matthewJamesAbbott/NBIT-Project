// delete item in receipt database
function deleteItem(itemId) {
  fetch("/delete-item", {
    method: "POST",
    body: JSON.stringify({ itemId: itemId }),
  }).then((_res) => {
    window.location.href = "/";
  });
}

// update database based on input from table in home template
function updateItem(rowId) {
  fetch("/update-item", {
  method: "POST",
  body: JSON.stringify(updateData),
  }).then((_res) => {
    window.location.href = "/";
  });
}

