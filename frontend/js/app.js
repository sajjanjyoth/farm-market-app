
function getDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // Earth radius in KM

    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;

    const a =
        Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(lat1 * Math.PI / 180) *
        Math.cos(lat2 * Math.PI / 180) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c;
}
// ===============================
// 🌍 MAP INITIALIZATION
// ===============================
let map = L.map('map').setView([12.2958, 76.6394], 13);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// ===============================
// 📍 GET USER LOCATION
// ===============================
if (navigator.geolocation) {

    navigator.geolocation.getCurrentPosition(

        async (pos) => {
            try {
                const userLat = pos.coords.latitude;
                const userLon = pos.coords.longitude;

                map.setView([userLat, userLon], 13);

                L.marker([userLat, userLon]).addTo(map)
                    .bindPopup("You are here 📍")
                    .openPopup();

                const res = await fetch(`${API_URL}/farmer/all`);

                if (!res.ok) {
                    throw new Error("API error: " + res.status);
                }

                const data = await res.json();
                console.log("Farmers API:", data);

                let farmers = Array.isArray(data) ? data : (data.farmers || []);

                farmers = farmers.filter(f => f.lat && f.lon);

                farmers.forEach(f => {
                    function getDistance(lat1, lon1, lat2, lon2) {
        const R = 6371;
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;

        const a =
            Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(lat1 * Math.PI / 180) *
            Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon / 2) * Math.sin(dLon / 2);

        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

        return R * c;
    }

                    const distance = getDistance(
                        userLat,
                        userLon,
                        f.lat,
                        f.lon
                    ).toFixed(2);

                    L.marker([f.lat, f.lon]).addTo(map)
                        .bindPopup(`
                            <b>${f.name}</b><br>
                            Distance: ${distance} km
                        `);
                });

            } catch (err) {
                console.error("Farmers fetch error:", err);
            }
        }
    );
}