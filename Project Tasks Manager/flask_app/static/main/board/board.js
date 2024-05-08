// Function to check new baord when create button is clicked
const checkNewBoard = function () {
    // Get the board name and emails from the input fields
    var name = $('#boardname').val();
    var emails = $('#memberemails').val();

    // Package data in a JSON object
    var data_d = { 'name': name, 'emails': emails };

    // Send data to server via AJAX
    $.ajax({
        url: "/processnewboard", // URL for the sign up processing endpoint
        data: data_d, // Data to be sent to the server
        type: "POST", // HTTP request type
        success: function (response) {
            // Parse the JSON response
            let result = JSON.parse(response);
            if (result.success === 1) {
                // Board creation successful, redirect to new board
                window.location.href = "/board?board_id=" + result.board_id;
            } else {
                // Board creation failed, update UI with error message
                alert('Unable To Create New Board.'); // Show alert
            }
        }
    });
}

document.addEventListener("DOMContentLoaded", function () {
    const addCardButtons = document.querySelectorAll(".list button");
    const lists = document.querySelectorAll(".list");

    let draggedCard;

    let count = 0;

    var socket = io.connect('https://' + document.domain + ':' + location.port + '/board?board_id=' + boardId);

    // Emit a 'joined' event when connected
    socket.on('connect', function () {
        socket.emit('live', { 'boardId': boardId });
    });

    // SocketIO event handler for card creation
    socket.on('card_created', function (data) {
        count++;
        const newCard = createCard(data.listId, count);
        lists[data.index].querySelector(".cards").appendChild(newCard);
        saveCardInfo(newCard, data.listId, '');
    });

    socket.on('card_text', function (data) {
        // Find the card element based on the card ID
        const cardId = data.cardId;
        const cardElement = document.querySelector(`.card[data-id="${cardId}"]`);

        // Update the card text content
        if (cardElement) {
            cardElement.querySelector(".cardText").value = data.cardText;
        }
    });

    socket.on('card_drop', function (data) {
        const listId = data.listId;
        const cardId = data.cardId;
        const cardElement = document.querySelector(`.card[data-id="${cardId}"]`);
        const listElement = document.getElementById(listId);
        if (listElement) {
            listElement.querySelector(".cards").appendChild(cardElement);
        }
    });

    socket.on('card_delete', function (data) {
        // Find the card element based on the card ID
        const cardId = data.cardId;
        const cardElement = document.querySelector(`.card[data-id="${cardId}"]`);

        // Delete card
        if (cardElement) {
            cardElement.remove();
        }
    });

    // Check if cards list is not empty
    if (allCards.length > 0) {
        // Loop through each card in the cards list
        allCards.forEach(function (card) {
            count++;
        });
    }

    const loadExistingCards = function (boardCards) {
        // Check if cards list is not empty
        if (boardCards.length > 0) {
            // Loop through each card in the cards list
            boardCards.forEach(function (card) {
                // Get the list ID of the card
                const listId = card.list_id;

                // Create a new card element
                const newCard = createCard(listId, card.card_id);

                // Set card text content
                newCard.querySelector(".cardText").value = card.text;

                // Append the new card to the corresponding list
                const list = document.getElementById(listId);
                if (list) {
                    list.querySelector(".cards").appendChild(newCard);
                }
            });
        }
    }

    loadExistingCards(boardCards);

    function createCard(listId, cardId) {
        const card = document.createElement("div");
        card.classList.add("card");
        card.setAttribute("draggable", "true");
        card.setAttribute("data-id", cardId);

        const cardBody = document.createElement("div");
        cardBody.classList.add("cardBody");

        const cardText = document.createElement("textarea");
        cardText.classList.add("cardText");
        cardText.setAttribute("placeholder", "Enter task details...");
        cardText.disabled = true;

        const cardButtons = document.createElement("div");
        cardButtons.classList.add("cardButtons");

        const editButton = document.createElement("button");
        editButton.textContent = "Edit";
        editButton.classList.add("cardEdit");

        editButton.addEventListener("click", function () {
            cardText.disabled = false;
            cardText.focus();
        });

        cardText.addEventListener("keydown", function (event) {
            if (event.key === "Enter") {
                event.preventDefault();
                cardText.disabled = true;
                const cardId = card.getAttribute("data-id"); // Get the card ID
                socket.emit('handle_text', { 'boardId': boardId, 'cardId': cardId, 'cardText': cardText.value });
                saveCardInfo(card, listId, cardText.value);
            }
        });

        const deleteButton = document.createElement("button");
        deleteButton.textContent = "Delete";
        deleteButton.classList.add("cardDelete");
        deleteButton.addEventListener("click", function () {
            const cardId = card.getAttribute("data-id"); // Get the card ID
            deleteCard(card, listId, cardText.value);
            socket.emit('handle_delete', { 'boardId': boardId, 'cardId': cardId })
        });

        cardBody.appendChild(cardText);
        cardButtons.appendChild(editButton);
        cardButtons.appendChild(deleteButton);

        card.appendChild(cardBody);
        card.appendChild(cardButtons);

        card.addEventListener("dragstart", dragStart);
        card.addEventListener("dragover", dragOver);

        return card;
    }

    const deleteCard = function (card, listId, newText) {
        // Get card ID
        const cardId = card.getAttribute("data-id");

        // Prepare data to be sent to the server
        const dataToSend = {
            cardId: cardId,
            cardText: newText,
            listId: listId,
            boardId: boardId
        };

        // Send data to server via AJAX
        $.ajax({
            url: "/processdeletecard", // URL for the delete card processing endpoint
            data: dataToSend, // Data to be sent to the server
            type: "POST", // HTTP request type
            success: function (response) {
                // Handle success response from server
                console.log("Card deleted successfully");
            }
        });
    }

    function dragStart(event) {
        draggedCard = event.target;
    }

    function dragOver(event) {
        event.preventDefault();
    }

    lists.forEach(function (list) {
        list.addEventListener("dragover", function (event) {
            event.preventDefault();
        });

        list.addEventListener("drop", function (event) {
            const newListId = list.id;
            const oldListId = draggedCard.closest(".list").id;
            if (oldListId !== newListId) {
                const cardText = draggedCard.querySelector(".cardText").value;
                saveCardInfo(draggedCard, newListId, cardText);
            }
            const cardId = draggedCard.getAttribute("data-id");
            socket.emit('handle_drop', { 'listId': list.id, 'boardId': boardId, 'cardId': cardId })
        });
    });

    addCardButtons.forEach(function (button, index) {
        button.addEventListener("click", function () {
            const listId = lists[index].id;
            socket.emit('new_card_created', { 'boardId': boardId, 'cardId': count, 'listId': listId, 'index': index, 'cardText': '' });
        });
    });

    function saveCardInfo(card, listId, newText) {
        // Get card ID
        const cardId = card.getAttribute("data-id");

        // Prepare data to be sent to the server
        const dataToSend = {
            cardId: cardId,
            cardText: newText,
            listId: listId,
            boardId: boardId
        };

        // Send data to server via AJAX
        $.ajax({
            url: "/processcardinfo", // URL for the card info processing endpoint
            data: dataToSend, // Data to be sent to the server
            type: "POST", // HTTP request type
            success: function (response) {
                // Handle success response from server
                console.log("Card info saved successfully");
            }
        });
    }
});




