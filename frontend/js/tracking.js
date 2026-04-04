const map=L.map('map').setView([15,75],7);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

let marker;

const socket=new WebSocket("ws://127.0.0.1:8000/ws/1");

socket.onmessage=(e)=>{
let d=JSON.parse(e.data);

if(marker)map.removeLayer(marker);

marker=L.marker([d.lat,d.lng]).addTo(map);
map.setView([d.lat,d.lng],15);
};