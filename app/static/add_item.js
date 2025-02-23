document.getElementById('add-item').addEventListener('click', async () => {
    try {
        const response = await fetch(`/add_item/${itemId}`, { method: 'POST' });
        const data = await response.json();
        if (data.success) {
            const newItem = data.item;
            document.getElementById('cart-items').insertAdjacentHTML('beforeend', `
                <div class="cart-item" data-item-id="${newItem.id}">
                    <span class="item-name">${newItem.name}</span>
                    <span class="item-price">${newItem.price}</span>
                    <button class="remove-item" data-item-id="${newItem.id}">Remove</button>
                </div>
            `);
        }
    } catch (error) {
        alert('Failed to add item.');
    }
});
