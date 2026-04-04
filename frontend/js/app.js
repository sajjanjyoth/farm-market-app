// ===============================
// 🌍 MAP INITIALIZATION
// ===============================
let map = L.map('map').setView([12.2958, 76.6394], 13);

// 🌐 OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png')
.addTo(map);


// ===============================
// 📍 GET USER LOCATION
// ===============================
navigator.geolocation.getCurrentPosition(

    // ✅ SUCCESS
    pos => {
        let userLat = pos.coords.latitude;
        let userLon = pos.coords.longitude;

        map.setView([userLat, userLon], 13);

        // 👤 User marker
        L.marker([userLat, userLon]).addTo(map)
            .bindPopup("You are here 📍")
            .openPopup();

        // 🌾 FETCH FARMERS
        fetch(API_URL + "/farmers")
        .then(res => res.json())
        .then(data => {

            console.log("Farmer API:", data); // 🔍 debug

            // ✅ Ensure array
            let farmers = Array.isArray(data) ? data : data.farmers || [];

            if (farmers.length === 0) {
                console.warn("No farmer found");
                return;
            }

            // ✅ SORT BY DISTANCE
            farmers.sort((a, b) =>
                getDistance(userLat, userLon, a.lat, a.lon) -
                getDistance(userLat, userLon, b.lat, b.lon)
            );

            // 📌 ADD MARKERS
            farmers.forEach(f => {

                let distance = getDistance(userLat, userLon, f.lat, f.lon).toFixed(2);

                L.marker([f.lat, f.lon]).addTo(map)
                .bindPopup(`
                    <b>${f.name}</b><br>
                    Distance: ${distance} km<br>
                    <button onclick="goToCategory('${f.category}')"
                    class="btn btn-sm btn-success mt-2">
                        View Products
                    </button>
                `);
            });

        })
        .catch(err => console.error("Farmers fetch error:", err));
    },

    // ❌ ERROR (Location denied)
    err => {
        alert("Location permission denied ❌");
    }
);


// ===============================
// 📏 DISTANCE (HAVERSINE)
// ===============================
function getDistance(lat1, lon1, lat2, lon2) {
    const R = 6371;

    let dLat = (lat2 - lat1) * Math.PI / 180;
    let dLon = (lon2 - lon1) * Math.PI / 180;

    let a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(lat1 * Math.PI / 180) *
        Math.cos(lat2 * Math.PI / 180) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);

    let c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c;
}


// ===============================
// 🔄 REDIRECT TO PRODUCTS
// ===============================
function goToCategory(cat) {
    window.location.href = "products.html?category=" + encodeURIComponent(cat);
}


// ===============================
// 👤 PROFILE SECTION
// ===============================

// 🔤 Get initials
function getInitials(name) {
    let words = name.split(" ");
    return (words[0][0] + (words[1] ? words[1][0] : "")).toUpperCase();
}

// 📦 Local storage
let username = localStorage.getItem("username");
let profileImage = localStorage.getItem("profileImage");

// 🎯 Elements
let avatar = document.getElementById("avatar");
let dropdown = document.getElementById("dropdownMenu");
let userNameText = document.getElementById("userName");
let logoutBtn = document.getElementById("logoutBtn");

// 👤 Show username
if (username && userNameText) {
    userNameText.innerText = username;
}

// 🧑 Avatar logic
if (avatar) {

    if (profileImage) {
        avatar.innerHTML = `
            <img src="${profileImage}" 
            style="width:35px;height:35px;border-radius:50%">
        `;
    } 
    else if (username) {
        avatar.innerText = getInitials(username);
    }

    // 🔽 Toggle dropdown
    avatar.onclick = () => {
        if (dropdown) {
            dropdown.style.display =
                dropdown.style.display === "block" ? "none" : "block";
        }
    };
}

// ❌ Close dropdown when clicking outside
window.onclick = function(e) {
    if (!e.target.closest(".profile-section") && dropdown) {
        dropdown.style.display = "none";
    }
};

// 🚪 Logout
if (logoutBtn) {
    logoutBtn.onclick = () => {
        localStorage.clear();
        window.location.href = "login.html";
    };
}