const socket = new WebSocket("ws://127.0.0.1:8000/ws/1");

socket.onopen = () => {
    console.log("Connected");
};

socket.onmessage = (event) => {
    console.log("Message:", event.data);
};

socket.onerror = (error) => {
    console.log("Error:", error);
};