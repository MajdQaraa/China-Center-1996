document.getElementById("resetForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const code = document.getElementById("code").value.trim();
    const newPassword = document.getElementById("newPassword").value.trim();

    try {
        const response = await fetch("/reset-password", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: email,
                code: code,
                new_password: newPassword
            })
        });

        const data = await response.json();

        if (data.success) {
            alert("Password reset successfully ✅");
            window.location.href = "log-in.html";
        } else {
            alert(data.message || "Invalid code ❌");
        }

    } catch (error) {
        console.error(error);
        alert("Server error ❌");
    }
});