const emailField2 = document.querySelector("#emailField");
const emailFeedbackArea2 = document.querySelector(".emailFeedbackArea");

emailField2.addEventListener("keyup", (e) => {
    emailField2.classList.remove("is-invalid");
    emailField2.classList.remove("is-valid");
    emailFeedbackArea2.style.display = "none";
    emailFeedbackArea2.innerHTML = ``;
    const emailVal = e.target.value;
    if (emailVal.length > 0) {
    fetch("/authentication/validate-email", {
        body: JSON.stringify({ email: emailVal }),
        method: "POST",
        })
        .then((res) => res.json())
        .then((data2) => {
            if (data2.email_error){
                emailField2.classList.add("is-invalid");
                emailFeedbackArea2.innerHTML = `<p>${data2.email_error}</p>`;
                emailFeedbackArea2.style.display = "block";
                submitBtn.disabled = true;
            } else {
                emailField2.classList.add("is-valid");
                emailField2.classList.remove("is-invalid");
                submitBtn.removeAttribute("disabled");
            }
        });
    }
});