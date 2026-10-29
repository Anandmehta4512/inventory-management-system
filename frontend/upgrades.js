// Advanced Frontend Enhancements (Trie Autocomplete & Low Stock Alerts)

async function setupSearchAutocomplete() {
    const searchInput = document.getElementById('search-input');
    if (!searchInput) return;

    // Create dropdown container
    const dropdown = document.createElement('div');
    dropdown.id = 'autocomplete-dropdown';
    dropdown.className = 'absolute bg-white border border-gray-200 shadow-lg rounded-md mt-1 w-full z-50 hidden';
    searchInput.parentNode.style.position = 'relative';
    searchInput.parentNode.appendChild(dropdown);

    searchInput.addEventListener('input', async (e) => {
        const query = e.target.value.trim();
        if (query.length < 1) {
            dropdown.classList.add('hidden');
            return;
        }

        try {
            const res = await fetch(`${API_URL}/api/search?q=${encodeURIComponent(query)}`);
            const items = await res.json();

            if (items.length === 0) {
                dropdown.classList.add('hidden');
                return;
            }

            dropdown.innerHTML = items.map(item => `
                <div class="p-2 hover:bg-gray-100 cursor-pointer text-sm flex justify-between">
                    <span class="font-medium text-gray-800">${item.name}</span>
                    <span class="text-gray-500">Stock: ${item.quantity}</span>
                </div>
            `).join('');
            dropdown.classList.remove('hidden');
        } catch (err) {
            console.error('Autocomplete error:', err);
        }
    });
}
