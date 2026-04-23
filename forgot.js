document.getElementById("forgotForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();

    try {
        const response = await fetch("https://china-center-1996.onrender.com/send-code", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email })
        });

        const data = await response.json();

        if (data.success) {
            alert("Code sent ✅");
window.location.href = "reset-password.html";
        } else {
            alert("Failed to send code ❌");
        }

    } catch (error) {
        alert("Server error ❌");
    }
});