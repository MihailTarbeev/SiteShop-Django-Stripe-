// Функционал для детальной страницы товара

document.addEventListener('DOMContentLoaded', function() {
    // Обработчики для кнопок количества
    setupQuantitySelector();
    
    // Анимация появления элементов
    setupAnimations();
    
    // Проверка авторизации при добавлении в корзину
    setupCartAuthCheck();
});

/**
 * Настройка кнопок + и - для выбора количества
 */
function setupQuantitySelector() {
    const quantityInput = document.querySelector('.quantity-input');
    const minusBtn = document.querySelector('.quantity-btn.minus');
    const plusBtn = document.querySelector('.quantity-btn.plus');
    
    if (minusBtn && plusBtn && quantityInput) {
        // Минус
        minusBtn.addEventListener('click', function() {
            let value = parseInt(quantityInput.value);
            if (value > 1) {
                quantityInput.value = value - 1;
            }
        });
        
        // Плюс
        plusBtn.addEventListener('click', function() {
            let value = parseInt(quantityInput.value);
            if (value < 99) {
                quantityInput.value = value + 1;
            }
        });
        
        // Валидация ввода
        quantityInput.addEventListener('change', function() {
            let value = parseInt(this.value);
            if (isNaN(value) || value < 1) {
                this.value = 1;
            } else if (value > 99) {
                this.value = 99;
            }
        });
        
        // Валидация при вводе с клавиатуры
        quantityInput.addEventListener('keydown', function(e) {
            // Разрешаем только цифры и управляющие клавиши
            if (!/[0-9]|Backspace|Delete|ArrowLeft|ArrowRight|Tab/.test(e.key)) {
                e.preventDefault();
            }
        });
    }
}

/**
 * Настройка анимаций появления
 */
function setupAnimations() {
    const elements = document.querySelectorAll('.item-detail-card > *');
    elements.forEach((el, index) => {
        el.style.animationDelay = `${index * 0.1}s`;
        el.style.animation = 'fadeIn 0.5s ease forwards';
        el.style.opacity = '0';
    });
}


/**
 * Показать сообщение об успешном добавлении в корзину
 */
function showCartSuccessMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'cart-success-message';
    messageDiv.innerHTML = `
        <svg class="success-icon" viewBox="0 0 24 24" width="20" height="20">
            <path fill="currentColor" d="M12 2C6.5 2 2 6.5 2 12S6.5 22 12 22 22 17.5 22 12 17.5 2 12 2M10 17L5 12L6.41 10.59L10 14.17L17.59 6.58L19 8L10 17Z"/>
        </svg>
        <span>Товар добавлен в корзину!</span>
    `;
    
    document.body.appendChild(messageDiv);
    
    // Показать сообщение
    setTimeout(() => {
        messageDiv.classList.add('show');
    }, 10);
    
    // Скрыть через 3 секунды
    setTimeout(() => {
        messageDiv.classList.remove('show');
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.parentNode.removeChild(messageDiv);
            }
        }, 300);
    }, 3000);
}

// Экспортируем функции для использования в других местах
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        setupQuantitySelector,
        setupAnimations,
        setupCartAuthCheck,
        showCartSuccessMessage
    };
}