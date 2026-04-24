document.getElementById("resetForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const emailInput = document.getElementById("email").value.trim();
    const code = document.getElementById("code").value.trim();
    const newPassword = document.getElementById("newPassword").value.trim();

    // 🔥 نجيب الإيميل من localStorage (إذا موجود)
    const savedEmail = localStorage.getItem("resetEmail");

    // إذا المستخدم ما كتب إيميل، نستخدم المخزن
    const email = emailInput || savedEmail;

    if (!email) {
        alert("Email is required ❌");
        return;
    }

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

            // 🔥 نحذف الإيميل المخزن
            localStorage.removeItem("resetEmail");

            window.location.href = "index.html";
        } else {
            alert(data.message || "Reset failed ❌");
        }

    } catch (error) {
        console.error(error);
        alert("Server error ❌");
    }
});