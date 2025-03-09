document.addEventListener('DOMContentLoaded', function() {
    const counterValueElement = document.getElementById('counter-value');
    const incrementButton = document.getElementById('increment-button');
    
    // Function to fetch the current counter value
    async function fetchCounter() {
        try {
            const response = await fetch('/api/counter');
            const data = await response.json();
            counterValueElement.textContent = data.value;
        } catch (error) {
            console.error('Error fetching counter:', error);
            counterValueElement.textContent = 'Error';
        }
    }
    
    // Function to increment the counter
    async function incrementCounter() {
        try {
            const response = await fetch('/api/counter/increment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            const data = await response.json();
            counterValueElement.textContent = data.value;
            
            // Add a brief animation effect
            counterValueElement.classList.add('updated');
            setTimeout(() => {
                counterValueElement.classList.remove('updated');
            }, 300);
        } catch (error) {
            console.error('Error incrementing counter:', error);
        }
    }
    
    // Add click event listener to the increment button
    incrementButton.addEventListener('click', incrementCounter);
    
    // Fetch the initial counter value
    fetchCounter();
});
