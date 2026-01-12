document.addEventListener('DOMContentLoaded', function() {
    const currentMonth = new Date().getMonth();
    if (currentMonth !== 11 && currentMonth !== 0) return;

    const snowContainer = document.createElement('div');
    snowContainer.id = 'snowflakes-container';
    snowContainer.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 99999;
        overflow: hidden;
    `;
    document.body.appendChild(snowContainer);

    const snowflakeCount = 15;
    const snowflakes = [];

    for (let i = 0; i < snowflakeCount; i++) {
        createSnowflake(i);
    }

    function createSnowflake(id) {
        const snowflake = document.createElement('div');
        const size = Math.random() * 10 + 15;
        
        snowflake.innerHTML = '❄';
        snowflake.style.cssText = `
            position: absolute;
            color: rgba(200, 225, 255, 0.7);
            font-size: ${size}px;
            user-select: none;
            pointer-events: none;
            z-index: 99999;
            will-change: transform;
        `;
        
        snowContainer.appendChild(snowflake);
        
        let y;
        if (id < snowflakeCount / 3) {
            y = Math.random() * window.innerHeight * 0.3;
        } else if (id < snowflakeCount * 2 / 3) {
            y = Math.random() * window.innerHeight * 0.6;
        } else {
            y = Math.random() * window.innerHeight;
        }
        
        let x = Math.random() * window.innerWidth;
        const speed = Math.random() * 1.2 + 0.3;
        let rotation = Math.random() * 360;
        const rotationSpeed = (Math.random() - 0.5) * 0.3;
        let swayOffset = Math.random() * Math.PI * 2;
        const swayAmount = Math.random() * 1.5 + 0.5;
        
        snowflake.style.opacity = Math.random() * 0.5 + 0.4;
        
        snowflakes.push({
            element: snowflake,
            x: x,
            y: y,
            speed: speed,
            rotation: rotation,
            rotationSpeed: rotationSpeed,
            swayOffset: swayOffset,
            swayAmount: swayAmount,
            size: size
        });
        
        snowflake.style.transform = `translate(${x}px, ${y}px) rotate(${rotation}deg)`;
    }

    function animateSnowflakes() {
        for (const snowflake of snowflakes) {
            snowflake.y += snowflake.speed;
            snowflake.rotation += snowflake.rotationSpeed;
            snowflake.swayOffset += 0.01;
            
            if (snowflake.y > window.innerHeight + snowflake.size) {
                snowflake.y = -snowflake.size;
                snowflake.x = Math.random() * window.innerWidth;
                snowflake.swayOffset = Math.random() * Math.PI * 2;
            }
            
            const sway = Math.sin(snowflake.swayOffset) * snowflake.swayAmount;
            
            snowflake.element.style.transform = `
                translate(${snowflake.x + sway}px, ${snowflake.y}px)
                rotate(${snowflake.rotation}deg)
            `;
            

            const opacity = 0.3 + (0.5 * Math.min(1, snowflake.y / window.innerHeight));
            snowflake.element.style.opacity = Math.max(0.3, Math.min(0.8, opacity));
        }
        
        requestAnimationFrame(animateSnowflakes);
    }

    animateSnowflakes();

    window.addEventListener('resize', function() {
        for (const snowflake of snowflakes) {
            if (snowflake.x > window.innerWidth) {
                snowflake.x = window.innerWidth - 20;
            }
            if (snowflake.y > window.innerHeight) {
                snowflake.y = -snowflake.size;
            }
        }
    });
});