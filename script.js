const tg = window.Telegram.WebApp;
tg.expand();

const colorBg = document.getElementById('color-bg');
const colorText = document.getElementById('color-text');
const colorAccent = document.getElementById('color-accent');

const valBg = document.getElementById('val-bg');
const valText = document.getElementById('val-text');
const valAccent = document.getElementById('val-accent');

const sliderOpacity = document.getElementById('slider-opacity');
const valOpacity = document.getElementById('val-opacity');
const btnCreate = document.getElementById('btn-create');

const uploadBox = document.getElementById('upload-box');
const fileInput = document.getElementById('file-input');
const previewImg = document.getElementById('preview');
const uploadStatus = document.getElementById('upload-status');

let uploadedImageUrl = "";

colorBg.addEventListener('input', (e) => { valBg.textContent = e.target.value.toUpperCase(); });
colorText.addEventListener('input', (e) => { valText.textContent = e.target.value.toUpperCase(); });
colorAccent.addEventListener('input', (e) => { valAccent.textContent = e.target.value.toUpperCase(); });
sliderOpacity.addEventListener('input', (e) => { valOpacity.textContent = `${e.target.value}%`; });

uploadBox.addEventListener('click', (e) => {
    e.preventDefault();
    fileInput.click();
});

fileInput.addEventListener('change', (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const file = files[0];
    uploadStatus.textContent = "Обработка изображения...";
    btnCreate.disabled = true;

    const reader = new FileReader();
    reader.onload = function(event) {
        uploadedImageUrl = event.target.result;
        previewImg.src = uploadedImageUrl;
        previewImg.style.display = 'block';
        uploadStatus.textContent = "Изображение успешно добавлено!";
        btnCreate.disabled = false;
    };
    reader.onerror = function() {
        uploadStatus.textContent = "Ошибка чтения файла.";
        btnCreate.disabled = false;
    };
    
    reader.readAsDataURL(file);
});

btnCreate.addEventListener('click', () => {
    const bg = colorBg.value.replace('#', '');
    const text = colorText.value.replace('#', '');
    const accent = colorAccent.value.replace('#', '');
    const opacityVal = parseInt(sliderOpacity.value);
    const device = document.querySelector('input[name="device"]:checked').value;
    const alpha = Math.round((opacityVal / 100) * 255).toString(16).padStart(2, '0');
    
    let themeUrl = `https://t.me{bg}&text=${text}&accent=${accent}&opacity=${alpha}&platform=${device}`;
    
    const resultData = {
        url: themeUrl,
        bg: colorBg.value,
        text: colorText.value,
        accent: colorAccent.value,
        device: device,
        has_wallpaper: uploadedImageUrl ? "Да" : "Нет"
    };
    
    tg.sendData(JSON.stringify(resultData));
    tg.close();
});
