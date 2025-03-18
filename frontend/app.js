// Global variables
let currentView = 'search';
let searchResults = [];
let collection = [];
let wishlist = [];
let backendStatus = false;

// Backend API URL
const API_URL = 'http://localhost:8000';

// Initialize the application
async function init() {
    // Check backend status
    checkBackendStatus();
    setInterval(checkBackendStatus, 30000); // Check every 30 seconds

    // Load collection and wishlist
    await Promise.all([
        loadCollection(),
        loadWishlist()
    ]);

    // Add event listeners
    document.getElementById('search-form').addEventListener('submit', handleSearch);
    document.getElementById('collection-sort-by').addEventListener('change', handleCollectionSort);
    document.getElementById('wishlist-sort-by').addEventListener('change', handleWishlistSort);

    // Initialize filters
    initializeFilters();

    // Add card hover effect
    document.addEventListener('mousemove', handleCardHover);
}

// Check backend status
async function checkBackendStatus() {
    try {
        const response = await fetch(`${API_URL}/health`);
        backendStatus = response.ok;
        updateBackendStatus();
    } catch (error) {
        backendStatus = false;
        updateBackendStatus();
    }
}

// Update backend status indicator
function updateBackendStatus() {
    const statusElement = document.getElementById('backend-status');
    if (backendStatus) {
        statusElement.textContent = 'Backend Online';
        statusElement.className = 'backend-status online';
    } else {
        statusElement.textContent = 'Backend Offline';
        statusElement.className = 'backend-status offline';
    }
}

// Initialize filters
async function initializeFilters() {
    try {
        const response = await fetch(`${API_URL}/sets`);
        const sets = await response.json();
        const setFilter = document.getElementById('set-filter');
        
        sets.forEach(set => {
            const option = document.createElement('option');
            option.value = set;
            option.textContent = set;
            setFilter.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading sets:', error);
    }
}

// Reset filters
function resetFilters() {
    document.getElementById('rarity-filter').value = '';
    document.getElementById('set-filter').value = '';
    document.getElementById('min-price').value = '';
    document.getElementById('max-price').value = '';
    document.getElementById('sort-by').value = 'name-asc';
    
    // Trigger search with reset filters
    handleSearch(new Event('submit'));
}

// Handle search form submission
async function handleSearch(event) {
    event.preventDefault();
    
    const searchQuery = document.querySelector('#search-form input').value;
    const rarity = document.getElementById('rarity-filter').value;
    const set = document.getElementById('set-filter').value;
    const minPrice = document.getElementById('min-price').value;
    const maxPrice = document.getElementById('max-price').value;
    const sortBy = document.getElementById('sort-by').value;
    
    try {
        const response = await fetch(`${API_URL}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: searchQuery,
                rarity: rarity,
                set: set,
                minPrice: minPrice,
                maxPrice: maxPrice,
                sortBy: sortBy
            })
        });
        
        searchResults = await response.json();
        displayCards(searchResults, 'search-results');
    } catch (error) {
        console.error('Error searching cards:', error);
        showError('Failed to search cards. Please try again.');
    }
}

// Handle collection sorting
function handleCollectionSort() {
    const sortBy = document.getElementById('collection-sort-by').value;
    sortAndDisplayCards(collection, 'collection-cards', sortBy);
}

// Handle wishlist sorting
function handleWishlistSort() {
    const sortBy = document.getElementById('wishlist-sort-by').value;
    sortAndDisplayCards(wishlist, 'wishlist-cards', sortBy);
}

// Sort and display cards
function sortAndDisplayCards(cards, containerId, sortBy) {
    const [criteria, order] = sortBy.split('-');
    const sortedCards = [...cards].sort((a, b) => {
        let valueA = a[criteria];
        let valueB = b[criteria];
        
        if (criteria === 'price') {
            valueA = parseFloat(valueA);
            valueB = parseFloat(valueB);
        }
        
        if (order === 'asc') {
            return valueA > valueB ? 1 : -1;
        } else {
            return valueA < valueB ? 1 : -1;
        }
    });
    
    displayCards(sortedCards, containerId);
}

// Display cards in the specified container
function displayCards(cards, containerId) {
    const container = document.getElementById(containerId);
    const isWishlist = containerId === 'wishlist-cards';
    
    if (!cards.length) {
        container.innerHTML = `
            <div class="text-center text-secondary my-5">
                <i class="fas fa-search fa-3x mb-3"></i>
                <h5>No cards found</h5>
                <p>Try adjusting your search criteria</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <div class="row row-cols-6 g-4">
            ${cards.map(card => `
                <div class="col">
                    <div class="card pokemon-card h-100">
                        <img src="${card.image}" class="card-img-top" alt="${card.name}">
                        <button class="wishlist-btn" onclick="toggleWishlist('${card.id}')">
                            <i class="fas fa-gift"></i>
                        </button>
                        <div class="card-body">
                            <h5 class="card-title">${card.name}</h5>
                            <div class="type-and-rarity-tags">
                                <span class="type-tag type-${card.type.toLowerCase()}">${card.type}</span>
                                <span class="rarity-tag rarity-${card.rarity.toLowerCase().replace(' ', '-')}">${card.rarity}</span>
                            </div>
                            <p class="card-text">Set: ${card.set}</p>
                            <p class="card-text">Price: $${card.price}</p>
                            <div class="card-actions">
                                <button class="btn btn-sm btn-primary" onclick="showCardDetails('${card.id}')">
                                    <i class="fas fa-info-circle"></i>
                                </button>
                                ${isWishlist ? `
                                    <button class="btn btn-sm btn-success" onclick="addToCollection('${card.id}')">
                                        Add
                                    </button>
                                    <button class="btn btn-sm btn-danger" onclick="removeFromWishlist('${card.id}')">
                                        Remove
                                    </button>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

// Show card details in modal
async function showCardDetails(cardId) {
    try {
        const response = await fetch(`${API_URL}/cards/${cardId}`);
        const card = await response.json();
        
        const modal = document.getElementById('modal');
        const modalTitle = modal.querySelector('.modal-title');
        const modalBody = modal.querySelector('.modal-body');
        
        modalTitle.textContent = card.name;
        modalBody.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <img src="${card.image}" class="img-fluid rounded" alt="${card.name}">
                </div>
                <div class="col-md-6">
                    <div class="mb-4">
                        <div class="type-and-rarity-tags mb-3">
                            <span class="type-tag type-${card.type.toLowerCase()}">${card.type}</span>
                            <span class="rarity-tag rarity-${card.rarity.toLowerCase().replace(' ', '-')}">${card.rarity}</span>
                        </div>
                        <div class="info-row mb-2">
                            <span class="info-label">Set:</span>
                            <span class="info-value">${card.set}</span>
                        </div>
                        <div class="info-row mb-2">
                            <span class="info-label">Number:</span>
                            <span class="info-value">${card.number}</span>
                        </div>
                        <div class="info-row mb-2">
                            <span class="info-label">Artist:</span>
                            <span class="info-value">${card.artist}</span>
                        </div>
                        <div class="info-row mb-2">
                            <span class="info-label">Release Date:</span>
                            <span class="info-value">${card.releaseDate}</span>
                        </div>
                        <div class="info-row mb-4">
                            <span class="info-label">Price:</span>
                            <span class="info-value">$${card.price}</span>
                        </div>
                    </div>
                    <div class="d-flex gap-2">
                        ${!collection.find(c => c.id === card.id) ? `
                            <button class="btn btn-primary" onclick="addToCollection('${card.id}')">
                                Add
                            </button>
                        ` : ''}
                        <button class="btn btn-outline-light" onclick="toggleWishlist('${card.id}')">
                            ${wishlist.find(c => c.id === card.id) ? 'Remove from Wishlist' : 'Add to Wishlist'}
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        modal.classList.add('show');
        
        // Close modal when clicking outside
        modal.addEventListener('click', (event) => {
            if (event.target === modal) {
                closeModal();
            }
        });
    } catch (error) {
        console.error('Error loading card details:', error);
        showError('Failed to load card details. Please try again.');
    }
}

// Close modal
function closeModal() {
    const modal = document.getElementById('modal');
    modal.classList.remove('show');
}

// Add card to collection
async function addToCollection(cardId) {
    try {
        const response = await fetch(`${API_URL}/collection/${cardId}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            await loadCollection();
            showSuccess('Card added to collection!');
            closeModal();
        } else {
            throw new Error('Failed to add card to collection');
        }
    } catch (error) {
        console.error('Error adding card to collection:', error);
        showError('Failed to add card to collection. Please try again.');
    }
}

// Toggle card in wishlist
async function toggleWishlist(cardId) {
    const isInWishlist = wishlist.find(card => card.id === cardId);
    
    try {
        const response = await fetch(`${API_URL}/wishlist/${cardId}`, {
            method: isInWishlist ? 'DELETE' : 'POST'
        });
        
        if (response.ok) {
            await loadWishlist();
            showSuccess(isInWishlist ? 'Card removed from wishlist!' : 'Card added to wishlist!');
        } else {
            throw new Error('Failed to update wishlist');
        }
    } catch (error) {
        console.error('Error updating wishlist:', error);
        showError('Failed to update wishlist. Please try again.');
    }
}

// Remove card from wishlist
async function removeFromWishlist(cardId) {
    try {
        const response = await fetch(`${API_URL}/wishlist/${cardId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            await loadWishlist();
            showSuccess('Card removed from wishlist!');
        } else {
            throw new Error('Failed to remove card from wishlist');
        }
    } catch (error) {
        console.error('Error removing card from wishlist:', error);
        showError('Failed to remove card from wishlist. Please try again.');
    }
}

// Load collection
async function loadCollection() {
    try {
        const response = await fetch(`${API_URL}/collection`);
        collection = await response.json();
        
        if (currentView === 'collection') {
            const sortBy = document.getElementById('collection-sort-by').value;
            sortAndDisplayCards(collection, 'collection-cards', sortBy);
            updateStats();
        }
    } catch (error) {
        console.error('Error loading collection:', error);
        showError('Failed to load collection. Please try again.');
    }
}

// Load wishlist
async function loadWishlist() {
    try {
        const response = await fetch(`${API_URL}/wishlist`);
        wishlist = await response.json();
        
        if (currentView === 'wishlist') {
            const sortBy = document.getElementById('wishlist-sort-by').value;
            sortAndDisplayCards(wishlist, 'wishlist-cards', sortBy);
        }
    } catch (error) {
        console.error('Error loading wishlist:', error);
        showError('Failed to load wishlist. Please try again.');
    }
}

// Show view
function showView(view) {
    // Update navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('onclick').includes(view)) {
            link.classList.add('active');
        }
    });
    
    // Hide all views
    document.querySelectorAll('.view').forEach(v => v.style.display = 'none');
    
    // Show selected view
    document.getElementById(`${view}-view`).style.display = 'block';
    
    currentView = view;
    
    // Load view-specific data
    switch (view) {
        case 'collection':
            loadCollection();
            break;
        case 'wishlist':
            loadWishlist();
            break;
        case 'stats':
            updateStats();
            break;
        case 'discover':
            loadDiscover();
            break;
    }
}

// Update statistics
function updateStats() {
    // Update overview stats
    document.getElementById('total-cards').textContent = collection.length;
    document.getElementById('unique-cards').textContent = new Set(collection.map(card => card.id)).size;
    
    const totalValue = collection.reduce((sum, card) => sum + parseFloat(card.price), 0);
    document.getElementById('total-value').textContent = `$${totalValue.toFixed(2)}`;
    
    const avgValue = totalValue / collection.length || 0;
    document.getElementById('avg-value').textContent = `$${avgValue.toFixed(2)}`;
    
    // Update charts
    updateValueChart();
    updateRarityChart();
    updateSetStats();
    updateValuableCards();
}

// Update value chart
function updateValueChart() {
    const ctx = document.getElementById('valueChart').getContext('2d');
    
    // Sample data - replace with actual historical data
    const data = {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [{
            label: 'Collection Value',
            data: [1000, 1050, 1100, 1075, 1200, 1150, 1300],
            borderColor: '#4361ee',
            backgroundColor: 'rgba(67, 97, 238, 0.1)',
            fill: true
        }]
    };
    
    new Chart(ctx, {
        type: 'line',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Update rarity chart
function updateRarityChart() {
    const ctx = document.getElementById('rarityChart').getContext('2d');
    
    const rarityCount = collection.reduce((acc, card) => {
        acc[card.rarity] = (acc[card.rarity] || 0) + 1;
        return acc;
    }, {});
    
    const data = {
        labels: Object.keys(rarityCount),
        datasets: [{
            data: Object.values(rarityCount),
            backgroundColor: [
                '#808080',
                '#27ae60',
                '#2980b9',
                '#8e44ad',
                '#d35400',
                '#c0392b',
                '#f39c12'
            ]
        }]
    };
    
    new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                }
            }
        }
    });
}

// Update set statistics
function updateSetStats() {
    const setCount = collection.reduce((acc, card) => {
        acc[card.set] = (acc[card.set] || 0) + 1;
        return acc;
    }, {});
    
    const setStats = document.getElementById('set-stats');
    setStats.innerHTML = `
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Set</th>
                        <th>Cards</th>
                        <th>Progress</th>
                    </tr>
                </thead>
                <tbody>
                    ${Object.entries(setCount)
                        .sort(([, a], [, b]) => b - a)
                        .map(([set, count]) => `
                            <tr>
                                <td>${set}</td>
                                <td>${count}</td>
                                <td>
                                    <div class="progress">
                                        <div class="progress-bar" style="width: ${(count / collection.length * 100)}%"></div>
                                    </div>
                                </td>
                            </tr>
                        `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

// Update valuable cards
function updateValuableCards() {
    const valuableCards = [...collection]
        .sort((a, b) => parseFloat(b.price) - parseFloat(a.price))
        .slice(0, 5);
    
    const valuableCardsElement = document.getElementById('valuable-cards');
    valuableCardsElement.innerHTML = `
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Card</th>
                        <th>Set</th>
                        <th>Rarity</th>
                        <th>Price</th>
                    </tr>
                </thead>
                <tbody>
                    ${valuableCards.map(card => `
                        <tr>
                            <td>${card.name}</td>
                            <td>${card.set}</td>
                            <td>
                                <span class="rarity-tag rarity-${card.rarity.toLowerCase().replace(' ', '-')}">
                                    ${card.rarity}
                                </span>
                            </td>
                            <td>$${card.price}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

// Load discover view
async function loadDiscover() {
    try {
        const response = await fetch(`${API_URL}/discover`);
        const data = await response.json();
        
        const discoverView = document.getElementById('discover-view');
        discoverView.innerHTML = `
            <h2 class="mb-4">Discover</h2>
            
            <!-- Featured Cards -->
            <section class="mb-5">
                <h3 class="mb-4">Featured Cards</h3>
                <div class="row row-cols-6 g-4">
                    ${data.featured.map(card => `
                        <div class="col">
                            <div class="card pokemon-card h-100">
                                <img src="${card.image}" class="card-img-top" alt="${card.name}">
                                <button class="wishlist-btn" onclick="toggleWishlist('${card.id}')">
                                    <i class="fas fa-gift"></i>
                                </button>
                                <div class="card-body">
                                    <h5 class="card-title">${card.name}</h5>
                                    <div class="type-and-rarity-tags">
                                        <span class="type-tag type-${card.type.toLowerCase()}">${card.type}</span>
                                        <span class="rarity-tag rarity-${card.rarity.toLowerCase().replace(' ', '-')}">${card.rarity}</span>
                                    </div>
                                    <p class="card-text">Set: ${card.set}</p>
                                    <p class="card-text">Price: $${card.price}</p>
                                    <div class="card-actions">
                                        <button class="btn btn-sm btn-primary" onclick="showCardDetails('${card.id}')">
                                            <i class="fas fa-info-circle"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </section>
            
            <!-- New Releases -->
            <section class="mb-5">
                <h3 class="mb-4">New Releases</h3>
                <div class="row row-cols-6 g-4">
                    ${data.newReleases.map(card => `
                        <div class="col">
                            <div class="card pokemon-card h-100">
                                <img src="${card.image}" class="card-img-top" alt="${card.name}">
                                <button class="wishlist-btn" onclick="toggleWishlist('${card.id}')">
                                    <i class="fas fa-gift"></i>
                                </button>
                                <div class="card-body">
                                    <h5 class="card-title">${card.name}</h5>
                                    <div class="type-and-rarity-tags">
                                        <span class="type-tag type-${card.type.toLowerCase()}">${card.type}</span>
                                        <span class="rarity-tag rarity-${card.rarity.toLowerCase().replace(' ', '-')}">${card.rarity}</span>
                                    </div>
                                    <p class="card-text">Set: ${card.set}</p>
                                    <p class="card-text">Price: $${card.price}</p>
                                    <div class="card-actions">
                                        <button class="btn btn-sm btn-primary" onclick="showCardDetails('${card.id}')">
                                            <i class="fas fa-info-circle"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </section>
            
            <!-- Trending Cards -->
            <section>
                <h3 class="mb-4">Trending Cards</h3>
                <div class="row row-cols-6 g-4">
                    ${data.trending.map(card => `
                        <div class="col">
                            <div class="card pokemon-card h-100">
                                <img src="${card.image}" class="card-img-top" alt="${card.name}">
                                <button class="wishlist-btn" onclick="toggleWishlist('${card.id}')">
                                    <i class="fas fa-gift"></i>
                                </button>
                                <div class="card-body">
                                    <h5 class="card-title">${card.name}</h5>
                                    <div class="type-and-rarity-tags">
                                        <span class="type-tag type-${card.type.toLowerCase()}">${card.type}</span>
                                        <span class="rarity-tag rarity-${card.rarity.toLowerCase().replace(' ', '-')}">${card.rarity}</span>
                                    </div>
                                    <p class="card-text">Set: ${card.set}</p>
                                    <p class="card-text">Price: $${card.price}</p>
                                    <div class="card-actions">
                                        <button class="btn btn-sm btn-primary" onclick="showCardDetails('${card.id}')">
                                            <i class="fas fa-info-circle"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </section>
        `;
    } catch (error) {
        console.error('Error loading discover view:', error);
        showError('Failed to load discover view. Please try again.');
    }
}

// Show success message
function showSuccess(message) {
    // Implement toast or notification system
    console.log('Success:', message);
}

// Show error message
function showError(message) {
    // Implement toast or notification system
    console.error('Error:', message);
}

// Handle card hover effect
function handleCardHover(e) {
    const cards = document.getElementsByClassName('pokemon-card');
    
    for (const card of cards) {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        card.style.setProperty('--mouse-x', `${x}px`);
        card.style.setProperty('--mouse-y', `${y}px`);
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', init);
