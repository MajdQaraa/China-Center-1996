document.getElementById("signupForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const confirmPassword = document.getElementById("confirmPassword").value.trim();

    // 🔒 تحقق بسيط
    if (!email || !password || !confirmPassword) {
        alert("Please fill all fields ❌");
        return;
    }

    if (password !== confirmPassword) {
        alert("Passwords do not match ❌");
        return;
    }

    try {
        const response = await fetch("/signup", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, password })
        });

        // 🔥 مهم جدًا: اطبع الرد
        const data = await response.json();
        console.log("SERVER RESPONSE:", data);

        if (data.success) {
            alert("Account created successfully ✅");
            window.location.href = "index.html"; // 🔥 عدلتها (أنت عامل login = index)
        } else {
            alert(data.message || "Signup failed ❌");
        }

    } catch (error) {
        console.error("ERROR:", error);
        alert("Server error ❌ (check console)");
    }
});