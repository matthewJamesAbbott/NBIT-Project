    function updateItem(itemId) {
        // Collect data from the edited table
        var tableData = [];
        $('#editableTable tbody tr').each(function () {
            var rowData = [];
            $(this).find('td[contenteditable="true"]').each(function () {
                rowData.push($(this).text());
            });
            tableData.push(rowData);
        });

        // Send data to the flask server using AJAX
        $.ajax({
            type: 'POST',
            url: '/update_data',  // Update this URL with your Flask route
            contentType: 'application/json;charset=UTF-8',
            data: JSON.stringify({ 'itemId': itemId, 'tableData': tableData }),
            success: function (response) {
                // Handle the response from the server if needed
                console.log(response);
            },
            error: function (error) {
                // Handle the error if needed
                console.error(error);
            }
        });
    }

