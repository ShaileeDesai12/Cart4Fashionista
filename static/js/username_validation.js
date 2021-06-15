const usernameField = document.querySelector("#usernameField");
const feedbackArea = document.querySelector(".invalid_feedback")
const submitBtn = document.querySelector(".submit-btn");

usernameField.addEventListener("keyup", (e) => {
    usernameField.classList.remove("is-invalid");
    usernameField.classList.remove("is-valid");
    feedbackArea.style.display = "none";
    feedbackArea.innerHTML = ``;
    const usernameVal = e.target.value;
    if (usernameVal.length > 0) {
    fetch("authenticate/validate-username", {
        body: JSON.stringify({ username: usernameVal }),
        method: "POST",
        })
        .then((res) => res.json())
        .then((data) => {
            if (data.username_error){
                usernameField.classList.add("is-invalid");
                feedbackArea.innerHTML = `<p>${data.username_error}</p>`;
                feedbackArea.style.display = "block";
                submitBtn.disabled = true;
            } else {
                usernameField.classList.add("is-valid");
                usernameField.classList.remove("is-invalid");
                submitBtn.removeAttribute("disabled");
            }
        });
    }
});