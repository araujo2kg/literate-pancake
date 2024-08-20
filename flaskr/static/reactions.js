document.querySelectorAll(".reaction-form").forEach(function (form) {
	form.addEventListener("submit", function (event) {
		// Stops the form post from executing
		event.preventDefault();
		let url = new URL(event.target.action);
		let [, reaction, post_id] = url.pathname.split("/");
		// Assync post request, credentials are required to pass in the session cookies
		fetch(`/${reaction}/${post_id}/reaction`, {
			method: "POST",
			credentials: "include",
			redirect: "manual",
		})
			.then((response) => {
				if (response.type === "opaqueredirect") {
					window.location.href = "/auth/login";
				} else {
					return response;
				}
			})
			// Data sent is incorrect
			.then((response) => {
				if (!response.ok) {
					alert("Invalid operation.");
				}
				return response.text();
			})
			// Update the buttons accordingly
			.then((message) => {
				let button =
					event.target.children[0].classList[0] == "like-button"
						? "activated-like"
						: "activated-dislike";
				let [txt, value] = event.target.children[0].value.split("|");
				value = parseInt(value);

				if (message.includes("registered")) {
					// Apply the class
					event.target.children[0].classList.add(button);
					event.target.children[0].value = txt + "| " + (value + 1);
				} else if (message.includes("deleted")) {
					event.target.children[0].classList.remove(button);
					event.target.children[0].value = txt + "| " + (value - 1);
				} else if (message.includes("updated")) {
					event.target.children[0].classList.add(button);
					event.target.children[0].value = txt + "| " + (value + 1);
					// Update the opposite button
					let button_id = event.target.children[0].dataset.buttonId;
					if (button == "activated-like") {
						let buttons = document.querySelectorAll(
							`input[data-button-id="${button_id}"]`,
						);
						buttons.forEach((button) => {
							if (button.classList[0] == "dislike-button") {
								button.classList.remove("activated-dislike");
								var [name, number] = button.value.split("|");
								button.value =
									name + "| " + (parseInt(number) - 1);
							}
						});
					} else if (button == "activated-dislike") {
						let buttons = document.querySelectorAll(
							`input[data-button-id="${button_id}"]`,
						);
						buttons.forEach((button) => {
							if (button.classList[0] == "like-button") {
								button.classList.remove("activated-like");
								var [name, number] = button.value.split("|");
								button.value =
									name + "| " + (parseInt(number) - 1);
							}
						});
					}
				}
			});
	});
});
