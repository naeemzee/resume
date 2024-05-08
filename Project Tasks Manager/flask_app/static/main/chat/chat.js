// Execute when the document is ready
$(document).ready(function () {

    // Connect to the SocketIO server
    socket = io.connect('https://' + document.domain + ':' + location.port + '/board?board_id=' + boardId);

    // Emit a 'joined' event when connected
    socket.on('connect', function () {
        socket.emit('joined', { 'boardId': boardId });
    });

    // Handle status messages received from the server
    socket.on('status', function (data) {
        // Create a new paragraph element
        let tag = document.createElement("p");
        // Create a text node with the message content
        let text = document.createTextNode(data.msg);
        // Get the chat container element
        let element = document.getElementById("chat");
        // Append the text node to the paragraph element
        tag.appendChild(text);
        // Apply CSS style to the paragraph element
        tag.style.cssText = data.style;
        // Append the paragraph element to the chat container
        element.appendChild(tag);
        // Scroll to the bottom of the chat container
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
    });

    // Handle chat messages received from the server
    socket.on('message', function (data) {
        // Create a new paragraph element
        let tag = document.createElement("p");
        // Create a text node with the message content
        let text = document.createTextNode(data.msg);
        // Get the chat container element
        let element = document.getElementById("chat");
        // Append the text node to the paragraph element
        tag.appendChild(text);
        // Apply CSS style to the paragraph element
        tag.style.cssText = data.style;
        // Append the paragraph element to the chat container
        element.appendChild(tag);
        // Scroll to the bottom of the chat container
        $('#chat').scrollTop($('#chat')[0].scrollHeight);
    });

    // Handle form submission to send messages
    $('form').submit(function (event) {
        event.preventDefault(); // Prevent default form submission
        var message = $('input[name=message]').val(); // Get the message from the input field
        socket.emit('message', { 'message': message, 'boardId': boardId }); // Send the message via SocketIO
        $('input[name=message]').val(''); // Clear the input field after sending
        return false;
    });

    // Handle clicking on the leave button
    $('#leave').click(function () {
        socket.emit('handle_disconnect', { 'boardId': boardId }); // Emit 'handle_disconnect' event to the server
        window.location.href = '/home';
    });

    // Function to emit a message when the user leaves the page or refreshes it
    window.onbeforeunload = function () {
        socket.emit('handle_disconnect', { 'boardId': boardId });
    };
});
