document.getElementById("loginForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const rememberMe = document.getElementById("rememberMe").checked;

    try {
        const response = await fetch("https://china-center-1996.onrender.com/login", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (data.success) {

            if (rememberMe) {
                localStorage.setItem("loggedIn", "true");
            } else {
                sessionStorage.setItem("loggedIn", "true");
            }

            window.location.href = "home.html";

        } else {
            alert("Wrong email or password ❌");
        }

    } catch (error) {
        alert("Server error ❌");
    }
});