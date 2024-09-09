const video = document.getElementById('video');
const output = document.getElementById('output');
const startCameraButton = document.getElementById('start-camera');
const captureButton = document.getElementById('capture');

startCameraButton.addEventListener('click', async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
});

captureButton.addEventListener('click', () => {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(async (blob) => {
        const formData = new FormData();
        formData.append('file', blob, 'snapshot.png');
        const response = await fetch('/upload/', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        if (result.status === 'success') {
            output.innerHTML = `Осталось отсканировать чанков: ${result.remaining_chunks}`;
        } else {
            output.innerHTML = `Ошибка: ${result.message}`;
        }
    }, 'image/png');
});