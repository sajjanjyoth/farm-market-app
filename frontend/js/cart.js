function addToCart(id){

    let qty = document.getElementById("qty-" + id).innerText;

    fetch(API_URL + "/cart", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": localStorage.getItem("token")
        },
        body: JSON.stringify({
            product_id: id,
            quantity: qty
        })
    })
    .then(res => res.json())
    .then(res => alert("Added to cart ✅"));
}