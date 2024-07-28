document.querySelectorAll(".reaction-form").forEach(function(form) {
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        let url = new URL(event.target.action);
        let [, reaction, post_id] = url.pathname.split("/");

    });
});