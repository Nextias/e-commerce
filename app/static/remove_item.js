document.getElementById('cart-items').addEventListener('click', async (event) => {
    if (event.target.classList.contains('remove-item')) {
        const itemId = event.target.dataset.itemId;
        try {
            const response = await fetch(`/remove_item/${itemId}`, { method: 'POST' });
            const data = await response.json();
            if (data.success) {
                document.querySelector(`.cart-item[data-item-id="${itemId}"]`).remove();
            }
        } catch (error) {
            alert('Failed to remove item.');
        }
    }
});