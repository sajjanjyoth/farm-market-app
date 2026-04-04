function pay(){
fetch(API_URL+"/create-payment",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({amount:500})
})
.then(res=>res.json())
.then(order=>{
const rzp=new Razorpay({
key:"YOUR_KEY",
amount:order.amount,
order_id:order.id,
handler:function(){alert("Success")}
});
rzp.open();
});
}