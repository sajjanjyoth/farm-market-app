function loadOrders() {

let token = localStorage.getItem("token");

if (!token) {
    alert("Login required");
    return;
}

fetch(API_URL + "/orders", {
    headers: {
        "Authorization": "Bearer " + token   // ✅ FIXED SPACE
    }
})
.then(res => res.json())
.then(data => {

    if (!Array.isArray(data)) {
        console.log(data);
        return;
    }

    let out = "";

    data.forEach(o => {
        out += `
        <div class="card mb-3 p-3 shadow-sm">
            <h6>Order ID: ${o.id}</h6>
            <p>Total: ₹${o.total}</p>

            <button onclick="downloadInvoice(${o.id})" 
            class="btn btn-sm btn-success">
            Download Invoice
            </button>
        </div>
        `;
    });

    document.getElementById("orders").innerHTML = out;
})
.catch(err => console.log(err));
}