// Function to update the product amount
async function add_product(productId, elementId, parentId) {
    try {
        // Send the product ID to the API
        const response = await fetch(`/backet/add_product/${productId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        if (!response.ok) {
            throw new Error('Failed to fetch updated product amount');
        }
        // Parse the response JSON
        const data = await response.json();
        // Get the new amount from the API response
        const newAmount = data.amount;
        // Update the amount displayed on the webpage
        const amountElement = document.getElementById(elementId);
        if (amountElement) {
            if (newAmount > 0){
            amountElement.textContent = newAmount;
            }
            else{
                parentElement = document.getElementById(parentId)
                parentElement.remove()
            }
        } else {
            console.error('Element not found');
        }
    } catch (error) {
        console.error('Error updating product amount:', error);
    }
}
