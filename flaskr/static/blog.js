document.querySelectorAll(".reaction-form").forEach(function(form) {
    form.addEventListener('submit', function(event) {
        // Stops the form post from executing
        event.preventDefault();
        let url = new URL(event.target.action);
        let [, reaction, post_id] = url.pathname.split("/");
        // Assync post request, credentials are required to pass in the session cookies
        fetch(`/${reaction}/${post_id}/reaction`, {
            method: 'POST',
            credentials: 'include',
            redirect: 'manual',
        })
        .then(response => {
            if (response.type === 'opaqueredirect') {
                window.location.href = '/auth/login';
            } else {
                return response;
            }
        })
        // Data sent is incorrect
        .then(response => {
            if (!response.ok) {
                alert('Invalid operation.')
            }
            return response.text();
        })
        // Update the buttons accordingly
        .then(message => {
            let button = event.target.children[0].value == "Like" ? "like-button" : "dislike-button"
            if (message.includes('registered')) {
               // Apply the class
               event.target.children[0].classList.add(button);
            }
            else if (message.includes('deleted')) {
               event.target.children[0].classList.remove(button);
            }
            else if (message.includes('updated')) {
                event.target.children[0].classList.add(button);
                // Update the opposite buttons
                let button_id = event.target.children[0].dataset.buttonId
                if (button == 'like-button') {
                    let buttons = document.querySelectorAll(`input[data-button-id="${button_id}"]`)
                    buttons.forEach(button => {
                        if (button.value == "Dislike") {
                            button.classList.remove('dislike-button');
                        }
                    });
               }
               else if (button == 'dislike-button') {
                    let buttons = document.querySelectorAll(`input[data-button-id="${button_id}"]`)
                    buttons.forEach(button => {
                        if (button.value == "Like") {
                            button.classList.remove('like-button');
                        }
                    });
               }
            }
        })
    });
});