let formData = new FormData();
formData.append("name", name);
formData.append("price", price);
formData.append("quantity", quantity);
formData.append("unit", unit);
formData.append("category", category);
formData.append("image", fileInput.files[0]);
fetch(API_URL + "/products")
.then(res => res.json())
.then(data => {

    let out = "";

    data.forEach(p => {

        out += `
        <div class="col-md-4 col-lg-3 mb-4">
            <div class="card shadow-sm h-100">

                <img src="${p.image}" 
                     class="card-img-top" 
                     style="height:180px; object-fit:cover;"
                     onerror="this.src='https://via.placeholder.com/200'">

                <div class="card-body d-flex flex-column">

                    <h6 class="fw-bold">${p.name}</h6>

                    <p class="text-success fw-bold mb-2">
                        ₹${p.price} ${p.unit ? '/ ' + p.unit : ''}
                    </p>

                    <button onclick="addToCart(${p.id})" 
                    class="btn btn-success mt-auto">
                        Add to Cart
                    </button>

                </div>

            </div>
        </div>
        `;
    });

    document.getElementById("products").innerHTML = out;
})
.catch(err => {
    console.error(err);
    alert("Failed to load products ❌");
});


// ✅ Add to cart
function addToCart(id){

    fetch(API_URL + "/cart", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": localStorage.getItem("token")
        },
        body: JSON.stringify({
            product_id: id,
            quantity: 1
        })
    })
    .then(res => res.json())
    .then(res => {
        alert(res.message || "Added to cart ✅");
    })
    .catch(err => {
        console.error(err);
        alert("Error adding to cart ❌");
    });
}