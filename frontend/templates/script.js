document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('task-form').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the form from submitting normally

        // Get form data
        var formData = new FormData(this);

        // Create a new table row
        var newRow = document.createElement('tr');
        newRow.innerHTML = `
            <td>${formData.get('name')}</td>
            <td>${formData.get('duration')}</td>
            <td>${formData.get('dependencies')}</td>
            <td>
                <button class="delete-btn">Delete</button>
            </td>
        `;

        // Append the new row to the table
        document.querySelector('#task-table tbody').appendChild(newRow);

        // Reset the form
        this.reset();
    });

    // Add event delegation for delete buttons
    document.getElementById('task-table').addEventListener('click', function(event) {
        if (event.target.classList.contains('delete-btn')) {
            event.target.closest('tr').remove();
        }
    });
});