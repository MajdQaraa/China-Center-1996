document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("forgotForm");

    if (!form) {
        console.error("Form not found ❌");
        return;
    }

    form.addEventListener("submit", async function(e) {
        e.preventDefault();

        const email = document.getElementById("email").value.trim();

        try {
            const response = await fetch("/send-code", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ email })
            });

            const data = await response.json();

            if (data.success) {

                if (data.code) {
                    alert("Your code: " + data.code);
                } else {
                    alert("Code sent to email ✅");
                }

                localStorage.setItem("resetEmail", email);
                window.location.href = "reset-password.html";

            } else {
                alert(data.message || "Failed ❌");
            }

        } catch (error) {
            console.error(error);
            alert("Server error ❌");
        }
    });

});