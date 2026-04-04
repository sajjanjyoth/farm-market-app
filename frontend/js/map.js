let currentLat, currentLng, map;

function initMap() {
    navigator.geolocation.getCurrentPosition(pos => {

        currentLat = pos.coords.latitude;
        currentLng = pos.coords.longitude;

        const userLoc = { lat: currentLat, lng: currentLng };

        map = new google.maps.Map(document.getElementById("map"), {
            zoom: 12,
            center: userLoc
        });

        new google.maps.Marker({
            position: userLoc,
            map: map,
            title: "You"
        });

        updateLocation(currentLat, currentLng);

        loadProducts(currentLat, currentLng, "All");
    });
}

// -------- UPDATE LOCATION --------
function updateLocation(lat, lng) {
    fetch("http://127.0.0.1:8000/user/location", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + localStorage.getItem("token")
        },
        body: JSON.stringify({ latitude: lat, longitude: lng })
    });
}

// -------- LOAD PRODUCTS --------
function loadProducts(lat, lng, category) {

    // Clear product list
    const list = document.getElementById("productList");
    list.innerHTML = "";

    fetch(`http://127.0.0.1:8000/nearby-products?user_lat=${lat}&user_lon=${lng}&category=${category}`)
    .then(res => res.json())
    .then(products => {

        products.forEach(p => {

            const marker = new google.maps.Marker({
                position: { lat: p.latitude, lng: p.longitude },
                map: map
            });

            const info = new google.maps.InfoWindow({
                content: `
                    <h3>${p.name}</h3>
                    <p>${p.category}</p>
                    <p>${p.distance_km} km</p>
                    <p>₹${p.price}</p>
                `
            });

            marker.addListener("click", () => info.open(map, marker));

            list.innerHTML += `
                <div style="border:1px solid #ccc; margin:10px; padding:10px;">
                    <h4>${p.name}</h4>
                    <p>${p.category}</p>
                    <p>${p.distance_km} km</p>
                    <p>₹${p.price}</p>
                </div>
            `;
        });
    });
}
// -------- RECOMMENDED --------
function loadRecommended(lat, lng) {
    fetch(`http://127.0.0.1:8000/recommended-farmer?user_lat=${lat}&user_lon=${lng}`)
    .then(res => res.json())
    .then(data => {
        if (data.farmer) {
            alert("Nearest Farmer: " + data.farmer.name + " (" + data.distance_km + " km)");
        }
    });
}