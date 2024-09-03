document.getElementById('uploadForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const files = document.getElementById('fileInput').files;

    const formData = new FormData();
    for (const file of files) {
        formData.append('files', file);
    }

    document.getElementById('status').textContent = 'Загрузка...';

    fetch('/upload', {
        method: 'POST',
        body: formData
    }).then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('status').textContent = 'Файл успешно восстановлен!';
            const downloadLink = document.getElementById('downloadLink');
            downloadLink.href = data.download_url;
            downloadLink.style.display = 'block';
        } else {
            document.getElementById('status').textContent = 'Ошибка: ' + data.error;
        }
    }).catch(error => {
        console.error('Error:', error);
        document.getElementById('status').textContent = 'Возникла ошибка при загрузке файлов.';
    });
});