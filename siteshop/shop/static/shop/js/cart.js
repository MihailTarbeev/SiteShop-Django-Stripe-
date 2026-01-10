document.addEventListener('DOMContentLoaded', function() {
    // Обработчики количества в корзине
    document.querySelectorAll('.qty-btn.minus').forEach(btn => {
        btn.addEventListener('click', function() {
            const input = this.closest('.update-quantity-form').querySelector('.qty-input');
            if (parseInt(input.value) > 1) {
                input.value = parseInt(input.value) - 1;
            }
        });
    });
    
    document.querySelectorAll('.qty-btn.plus').forEach(btn => {
        btn.addEventListener('click', function() {
            const input = this.closest('.update-quantity-form').querySelector('.qty-input');
            if (parseInt(input.value) < 99) {
                input.value = parseInt(input.value) + 1;
            }
        });
    });
    
    // Кнопка оформления заказа
    const checkoutBtn = document.getElementById('checkout-btn');
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', function() {
            alert('Функция оформления заказа будет реализована позже!');
            // Здесь будет редирект на оформление заказа
        });
    }
});