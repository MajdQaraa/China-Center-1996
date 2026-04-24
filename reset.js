document.getElementById("resetForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const code = document.getElementById("code").value;
    const newPassword = document.getElementById("newPassword").value;

    try {
        const res = await fetch("https://china-center-1996.up.railway.app/reset-password", {
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

        const data = await res.json();

        console.log("RESPONSE:", data); // 🔥 للتشخيص

        if (data.success) {
            alert("Password changed successfully ✅");

            // 🔥 يرجعك لصفحة تسجيل الدخول
            window.location.href = "index.html";
        } else {
            alert(data.message || "Something went wrong ❌");
        }

    } catch (error) {
        console.error("Error:", error);
        alert("Server error ❌");
    }
});