const API = "http://127.0.0.1:8000";

// ✅ REGISTER
function register() {
    const data = {
        name: document.getElementById("name")?.value,
        email: document.getElementById("email").value,
        password: document.getElementById("password").value,
        role: document.getElementById("role")?.value || "customer"
    };

    fetch(API + "/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(res => {
        if (res.message) {
            alert(res.message);
            window.location.href = "login.html";
        } else {
            alert(res.detail || "Registration failed");
        }
    })
    .catch(() => alert("Server error ❌"));
}


// ✅ LOGIN
function login() {
    const data = {
        email: document.getElementById("email").value,
        password: document.getElementById("password").value
    };

    fetch(API + "/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(res => {
        if (res.detail) {
            alert(res.detail);
            return;
        }

        localStorage.setItem("token", res.token);
        localStorage.setItem("user", JSON.stringify(res.user));

        alert("Login Successful ✅");
        window.location.href = "index.html";
    })
    .catch(() => alert("Login error ❌"));
}


// ✅ LOAD USER (Navbar)
function loadUser() {
    const user = JSON.parse(localStorage.getItem("user"));

    if (!user) return;

    document.getElementById("username").innerText = "Hi, " + user.name;

    document.getElementById("loginBtn")?.classList.add("d-none");
    document.getElementById("registerBtn")?.classList.add("d-none");
    document.getElementById("logoutBtn")?.classList.remove("d-none");

   
}
fetch("http://127.0.0.1:8000/users", {
    headers: {
        "Authorization": "Bearer " + localStorage.getItem("token")
    }
})

// ✅ LOGOUT
function logout() {
    localStorage.clear();
    window.location.href = "login.html";
}