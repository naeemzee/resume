// Initialize count variable to keep track of login attempts
let count = 0;

// Function to check user credentials when login button is clicked
const checkCredentials = function () {
    // Get the email and password from the input fields
    var email = $('#username').val();
    var password = $('#password').val();

    // Package data in a JSON object
    var data_d = { 'email': email, 'password': password };

    // Send data to server via AJAX
    $.ajax({
        url: "/processlogin", // URL for the login processing endpoint
        data: data_d, // Data to be sent to the server
        type: "POST", // HTTP request type
        success: function (response) {
            // Parse the JSON response
            let result = JSON.parse(response);
            if (result.success === 1) {
                // Authentication successful, redirect to home page
                window.location.href = "/home";
            } else {
                // Authentication failed, update UI with error message
                count++; // Increment login attempt count
                alert('Authentication failed. Attempts: ' + count); // Show alert with login attempt count
            }
        }
    });
}
