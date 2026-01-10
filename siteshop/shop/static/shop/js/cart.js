document.addEventListener('DOMContentLoaded', function() {
    console.log('Cart JS loaded');
    
    // Функция для преобразования строки с запятой в число
    function parseEuropeanNumber(str) {
        if (!str) return 0;
        
        // Заменяем запятую на точку и убираем пробелы
        const cleanStr = str.toString()
            .replace(/\./g, '')  // убираем точки как разделители тысяч
            .replace(/,/g, '.')  // заменяем запятую на точку
            .replace(/\s/g, ''); // убираем пробелы
        
        return parseFloat(cleanStr) || 0;
    }
    
    // Функция для форматирования числа в европейский формат
    function formatEuropeanNumber(num) {
        return num.toFixed(2).replace('.', ',');
    }
    
    // Вспомогательные функции для точных вычислений с деньгами
    function multiplyMoney(price, quantity) {
        // Преобразуем в центы и работаем с целыми числами
        const priceInCents = Math.round(price * 100);
        const totalInCents = priceInCents * quantity;
        return totalInCents / 100;
    }
    
    function sumMoney(numbers) {
        // Суммируем с точностью до центов
        let totalInCents = 0;
        numbers.forEach(num => {
            totalInCents += Math.round(num * 100);
        });
        return totalInCents / 100;
    }
    
    // 1. Храним оригинальные данные корзины
    let originalCartTotal = 0;
    let cartCurrency = '';
    
    // Получаем элементы
    const cartTotalElement = document.getElementById('cart-total');
    const totalQuantityElement = document.getElementById('total-quantity');
    
    // Получаем валюту из data-атрибута
    if (cartTotalElement && cartTotalElement.dataset.currency) {
        cartCurrency = cartTotalElement.dataset.currency;
        originalCartTotal = parseEuropeanNumber(cartTotalElement.dataset.originalTotal);
    } else if (cartTotalElement) {
        // Если нет data-атрибутов, пробуем парсить текст
        const totalText = cartTotalElement.textContent.trim();
        const parts = totalText.split(' ');
        
        if (parts.length >= 2) {
            originalCartTotal = parseEuropeanNumber(parts[0]);
            cartCurrency = parts.slice(1).join(' '); // Берем все после первого пробела
        }
    }
    
    console.log('Original cart total:', originalCartTotal, 'Currency:', cartCurrency);
    
    // 2. Собираем данные о товарах
    const cartItems = [];
    
    document.querySelectorAll('.cart-item-card').forEach(card => {
        const input = card.querySelector('.qty-input');
        const totalElement = card.querySelector('.total-price');
        
        // Получаем цену из data-атрибута, преобразуя запятую в точку
        const priceText = card.dataset.itemPrice || '';
        const price = parseEuropeanNumber(priceText);
        
        const currency = card.dataset.itemCurrency || '';
        
        // Парсим текущую сумму товара
        const totalText = totalElement.textContent.trim();
        const parts = totalText.split(' ');
        let originalItemTotal = 0;
        let itemCurrency = currency;
        
        if (parts.length >= 2) {
            originalItemTotal = parseEuropeanNumber(parts[0]);
            // Если currency из data-атрибута пустая, берем из текста
            if (!itemCurrency) {
                itemCurrency = parts.slice(1).join(' ');
            }
        }
        
        // Сохраняем данные
        cartItems.push({
            card: card,
            price: price,  // цена товара (например 9.99)
            currency: itemCurrency,
            originalQuantity: parseInt(input.value) || 1,
            currentQuantity: parseInt(input.value) || 1,
            input: input,
            totalElement: totalElement,
            originalTotal: originalItemTotal
        });
        
        // Сохраняем оригинальное значение
        input.dataset.originalValue = input.value;
    });
    
    // 3. Функция для обновления суммы товара с точностью
    function updateItemTotal(cartItem) {
        // Используем точное умножение через центы
        const itemTotal = multiplyMoney(cartItem.price, cartItem.currentQuantity);
        // Форматируем в европейский формат с запятой
        cartItem.totalElement.textContent = `${formatEuropeanNumber(itemTotal)} ${cartItem.currency}`;
        return itemTotal;
    }
    
    // 4. Функция для обновления общей суммы корзины с точностью
    function updateCartTotal() {
        if (!cartTotalElement || !cartCurrency) return;
        
        // Собираем суммы всех товаров
        const itemTotals = [];
        cartItems.forEach(item => {
            const itemTotal = multiplyMoney(item.price, item.currentQuantity);
            itemTotals.push(itemTotal);
        });
        
        // Суммируем с точностью
        const totalSum = sumMoney(itemTotals);
        
        // Форматируем в европейский формат с запятой
        cartTotalElement.textContent = `${formatEuropeanNumber(totalSum)} ${cartCurrency}`;
    }
    
    // 5. Функция для обновления общего количества
    function updateTotalQuantity() {
        if (!totalQuantityElement) return;
        
        let totalQuantity = 0;
        
        // Суммируем количество всех товаров
        cartItems.forEach(item => {
            totalQuantity += item.currentQuantity;
        });
        
        // Обновляем отображение
        totalQuantityElement.textContent = `${totalQuantity} шт.`;
    }
    
    // 6. Функция для изменения количества
    function handleQuantityChange(button, change) {
        const form = button.closest('.update-quantity-form');
        const input = form.querySelector('.qty-input');
        const card = button.closest('.cart-item-card');
        
        // Находим товар
        const cartItem = cartItems.find(item => item.card === card);
        if (!cartItem) return;
        
        let newQuantity = cartItem.currentQuantity + change;
        
        // Проверяем границы
        if (newQuantity < 1) {
            updateButtonState(input, true, false);
            return;
        }
        if (newQuantity > 99) {
            updateButtonState(input, false, true);
            return;
        }
        
        // Обновляем данные
        input.value = newQuantity;
        cartItem.currentQuantity = newQuantity;
        
        // Обновляем сумму товара (с точностью)
        updateItemTotal(cartItem);
        
        // Обновляем общие значения (с точностью)
        updateCartTotal();
        updateTotalQuantity();
        
        // Показываем кнопку "Обновить"
        showUpdateButton(form);
        
        // Обновляем состояние кнопок
        updateButtonState(input, newQuantity <= 1, newQuantity >= 99);
    }
    
    // 7. Функция для обновления состояния кнопок +/-
    function updateButtonState(input, isMinDisabled, isPlusDisabled) {
        const minusBtn = input.parentElement.querySelector('.minus');
        const plusBtn = input.parentElement.querySelector('.plus');
        
        if (minusBtn) {
            minusBtn.style.opacity = isMinDisabled ? '0.5' : '1';
            minusBtn.style.cursor = isMinDisabled ? 'not-allowed' : 'pointer';
            minusBtn.disabled = isMinDisabled;
        }
        
        if (plusBtn) {
            plusBtn.style.opacity = isPlusDisabled ? '0.5' : '1';
            plusBtn.style.cursor = isPlusDisabled ? 'not-allowed' : 'pointer';
            plusBtn.disabled = isPlusDisabled;
        }
    }
    
    // 8. Показать кнопку 
    function showUpdateButton(form) {
        const updateBtn = form.querySelector('.update-btn');
        if (updateBtn && updateBtn.style.display === 'none') {
            updateBtn.style.display = 'inline-block';
            updateBtn.style.backgroundColor = '#28a745'; 
            updateBtn.style.color = 'white'; 
        }
    }
    
    // 9. Обработчики для кнопок +/-
    document.querySelectorAll('.qty-btn.minus').forEach(btn => {
        btn.addEventListener('click', function() {
            handleQuantityChange(this, -1);
        });
    });
    
    document.querySelectorAll('.qty-btn.plus').forEach(btn => {
        btn.addEventListener('click', function() {
            handleQuantityChange(this, 1);
        });
    });
    
    // 10. Обработчик для стрелочек input[type=number]
    document.querySelectorAll('.qty-input').forEach(input => {
        const card = input.closest('.cart-item-card');
        const cartItem = cartItems.find(item => item.input === input);
        
        input.addEventListener('input', function() {
            const form = this.closest('.update-quantity-form');
            let newQuantity = parseInt(this.value) || 1;
            
            // Проверяем границы
            if (newQuantity < 1) {
                this.value = 1;
                newQuantity = 1;
            }
            if (newQuantity > 99) {
                this.value = 99;
                newQuantity = 99;
            }
            
            if (cartItem) {
                cartItem.currentQuantity = newQuantity;
                
                // Обновляем сумму товара (с точностью)
                updateItemTotal(cartItem);
                
                // Обновляем общие значения (с точностью)
                updateCartTotal();
                updateTotalQuantity();
                
                // Показываем кнопку если значение изменилось
                if (this.value !== this.dataset.originalValue) {
                    showUpdateButton(form);
                }
                
                // Обновляем состояние кнопок
                updateButtonState(this, newQuantity <= 1, newQuantity >= 99);
            }
        });
    });
    
    // 11. Кнопка оформления заказа
    const checkoutBtn = document.getElementById('checkout-btn');
    if (checkoutBtn && !checkoutBtn.disabled) {
        checkoutBtn.addEventListener('click', function(e) {
            // Проверяем есть ли несохраненные изменения
            const unsavedForms = Array.from(document.querySelectorAll('.update-quantity-form'))
                .filter(form => {
                    const updateBtn = form.querySelector('.update-btn');
                    return updateBtn && updateBtn.style.display !== 'none';
                });
            
            if (unsavedForms.length > 0) {
                e.preventDefault();
                if (confirm('У вас есть несохраненные изменения. Сохранить перед оформлением заказа?')) {
                    unsavedForms.forEach(form => form.submit());
                }
            }
        });
    }
    
    // 12. Скрываем кнопки "Обновить" при загрузке
    document.querySelectorAll('.update-btn').forEach(btn => {
        btn.style.display = 'none';
    });
    
    // 13. Инициализируем состояние всех кнопок
    document.querySelectorAll('.qty-input').forEach(input => {
        const quantity = parseInt(input.value) || 1;
        updateButtonState(input, quantity <= 1, quantity >= 99);
    });
    
});