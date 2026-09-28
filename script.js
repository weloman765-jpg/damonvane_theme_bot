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

// Обновление кодов палитры цветов интерфейса
colorBg.addEventListener('input', (e) => { valBg.textContent = e.target.value.toUpperCase(); });
colorText.addEventListener('input', (e) => { valText.textContent = e.target.value.toUpperCase(); });
colorAccent.addEventListener('input', (e) => { valAccent.textContent = e.target.value.toUpperCase(); });
sliderOpacity.addEventListener('input', (e) => { valOpacity.textContent = `${e.target.value}%`; });

// Клики по зоне загрузки картинки
uploadBox.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    uploadStatus.textContent = "Загрузка изображения на сервер...";
    btnCreate.disabled = true;

    // Загрузка через Imgur API
    const formData = new FormData();
    formData.append('image', file);

    try {
        const response = await fetch('https://imgur.com', {
            method: 'POST',
            headers: { Authorization: 'Client-ID 78efca0b1c0bc81' }, // Бесплатный публичный ID клиента Imgur
            body: formData
        });
        const resData = await response.json();
        if (resData.success) {
            uploadedImageUrl = resData.data.link;
            previewImg.src = uploadedImageUrl;
            previewImg.style.display = 'block';
            uploadStatus.textContent = "Изображение успешно добавлено!";
        } else {
            uploadStatus.textContent = "Ошибка загрузки. Попробуйте еще раз.";
        }
    } catch (err) {
        uploadStatus.textContent = "Ошибка сети хостинга картинок.";
    }
    btnCreate.disabled = false;
});

btnCreate.addEventListener('click', () => {
    const bg = colorBg.value.replace('#', '');
    const text = colorText.value.replace('#', '');
    const accent = colorAccent.value.replace('#', '');
    const opacityVal = parseInt(sliderOpacity.value);
    const device = document.querySelector('input[name="device"]:checked').value;
    const alpha = Math.round((opacityVal / 100) * 255).toString(16).padStart(2, '0');
    
    // Формируем прямую ссылку на установку темы Telegram с параметрами цветов и картинки
    let themeUrl = `https://t.me{bg}&text=${text}&accent=${accent}&opacity=${alpha}&platform=${device}`;
    if(uploadedImageUrl) {
        themeUrl += `&wallpaper=${encodeURIComponent(uploadedImageUrl)}`;
    }
    
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
