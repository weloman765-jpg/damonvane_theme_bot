// Инициализация Telegram Web App API
const tg = window.Telegram.WebApp;
tg.expand(); // Расширяем окно на весь экран телефона

// Получаем элементы интерфейса
const colorBg = document.getElementById('color-bg');
const colorText = document.getElementById('color-text');
const colorAccent = document.getElementById('color-accent');

const valBg = document.getElementById('val-bg');
const valText = document.getElementById('val-text');
const valAccent = document.getElementById('val-accent');

const sliderOpacity = document.getElementById('slider-opacity');
const valOpacity = document.getElementById('val-opacity');
const btnCreate = document.getElementById('btn-create');

// Слушатели обновлений палитры
colorBg.addEventListener('input', (e) => { valBg.textContent = e.target.value.toUpperCase(); });
colorText.addEventListener('input', (e) => { valText.textContent = e.target.value.toUpperCase(); });
colorAccent.addEventListener('input', (e) => { valAccent.textContent = e.target.value.toUpperCase(); });

// Слушатель ползунка прозрачности
sliderOpacity.addEventListener('input', (e) => {
    valOpacity.textContent = `${e.target.value}%`;
});

// Обработка клика по главной кнопке "Создать тему"
btnCreate.addEventListener('click', () => {
    const bg = colorBg.value.replace('#', '');
    const text = colorText.value.replace('#', '');
    const accent = colorAccent.value.replace('#', '');
    const opacityVal = parseInt(sliderOpacity.value);
    
    // Получаем выбранное устройство
    const device = document.querySelector('input[name="device"]:checked').value;
    
    // Переводим процент прозрачности в HEX формат (от 00 до FF)
    const alpha = Math.round((opacityVal / 100) * 255).toString(16).padStart(2, '0');
    
    // Сборка параметров темы в зависимости от платформы
    // Для демонстрации базовой логики используем стандартный паттерн параметров ссылки тем Telegram
    let themeUrl = `https://t.me{bg}&text=${text}&accent=${accent}&opacity=${alpha}&platform=${device}`;
    
    // Отправляем данные обратно нашему боту в чат
    const resultData = {
        url: themeUrl,
        bg: colorBg.value,
        text: colorText.value,
        accent: colorAccent.value,
        device: device
    };
    
    tg.sendData(JSON.stringify(resultData)); // Передаем объект боту
    tg.close(); // Закрываем веб-приложение
});
