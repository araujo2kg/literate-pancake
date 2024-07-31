        document.addEventListener("DOMContentLoaded", event => {
                document.body.addEventListener('click', event => {
                    if (event.target.name == 'toggle-comment') {
                    let post = event.target.getAttribute('data-toggle-comment')
                    let form = document.querySelector(`form[name="${post}"]`)
                    let display_property = window.getComputedStyle(form).display
                    if (display_property == 'none') {
                        form.style.display = 'flex'
                    } else {
                        form.style.display = 'none'
                    }
                }
            });
        });
 