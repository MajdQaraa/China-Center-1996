document.getElementById("signupForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const confirmPassword = document.getElementById("confirmPassword").value.trim();

    if (password !== confirmPassword) {
        alert("Passwords do not match ❌");
        return;
    }

    try {
        const response = await fetch("/signup", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (data.success) {
            alert("Account created successfully ✅");
            window.location.href = "log-in.html";
        } else {
            alert(data.message);
        }

    } catch (error) {
        alert("Server error ❌");
    }
});