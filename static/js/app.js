// Modern JavaScript for МЕТРИКС application

class App {
    constructor() {
        this.cart = [];
        this.minOrderQuantity = 100;
        this.products = [];
        this.categories = [];
        this.currentCategory = 'all';
        this.searchQuery = '';
        this.init();
    }

    init() {
        this.loadProducts();
        this.loadCart();
        this.updateCartCount();
        this.bindEvents();
        this.initializeAnimations();
    }

    loadProducts() {
        // Load products from server
        fetch('/catalog')
            .then(response => response.text())
            .then(html => {
                // Parse products from the page
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                
                // Extract products data from the page
                const productsData = doc.querySelector('#products-data');
                if (productsData) {
                    try {
                        this.products = JSON.parse(productsData.textContent);
                    } catch (e) {
                        console.error('Error parsing products data:', e);
                    }
                }
                
                // Extract categories data from the page
                const categoriesData = doc.querySelector('#categories-data');
                if (categoriesData) {
                    try {
                        this.categories = JSON.parse(categoriesData.textContent);
                    } catch (e) {
                        console.error('Error parsing categories data:', e);
                    }
                }
                
                this.renderProducts();
                this.renderCategories();
                this.handleURLParams();
            })
            .catch(error => {
                console.error('Error loading products:', error);
            });
    }

    renderProducts() {
        const productsContainer = document.getElementById('products-container');
        if (!productsContainer) {
            console.log('Products container not found');
            return;
        }

        console.log('Rendering products:', this.products.length);
        console.log('Current category:', this.currentCategory);
        console.log('Search query:', this.searchQuery);

        let filteredProducts = this.products;
        
        // Filter by category (only if a specific category is selected)
        if (this.currentCategory && this.currentCategory !== 'all') {
            filteredProducts = filteredProducts.filter(product => 
                product.category === this.currentCategory
            );
        }
        
        // Filter by search query
        if (this.searchQuery) {
            const query = this.searchQuery.toLowerCase();
            filteredProducts = filteredProducts.filter(product =>
                product.name.toLowerCase().includes(query) ||
                (product.description && product.description.toLowerCase().includes(query)) ||
                (product.brand && product.brand.toLowerCase().includes(query)) ||
                (product.sku && product.sku.toLowerCase().includes(query))
            );
        }

        console.log('Filtered products:', filteredProducts.length);

        if (filteredProducts.length === 0) {
            productsContainer.innerHTML = `
                <div class="col-12 text-center py-5">
                    <h4 class="text-muted">Товары не найдены</h4>
                    <p class="text-muted">Попробуйте изменить параметры поиска или категорию</p>
                </div>
            `;
            return;
        }

        const productsHTML = filteredProducts.map(product => `
            <div class="col-lg-4 col-md-6 mb-4">
                <div class="card product-card h-100 shadow-sm clickable-card" 
                     data-product-id="${product.id}" 
                     style="cursor: pointer; transition: all 0.3s ease;">
                    <div class="card-img-top-container" style="height: 250px; overflow: hidden; background: #f8f9fa;">
                        <img src="${product.image || '/static/images/bolts/bolt-silver.png'}" 
                             class="card-img-top product-image" 
                             alt="${product.name}"
                             style="width: 100%; height: 100%; object-fit: contain; padding: 15px;">
                    </div>
                    <div class="card-body d-flex flex-column">
                        <h5 class="card-title fw-bold text-primary mb-3">${product.name}</h5>
                        <p class="card-text flex-grow-1 text-muted mb-3">${product.description || ''}</p>
                        
                        <div class="product-specs mb-3">
                            <!-- Desktop view - always visible -->
                            <div class="d-none d-md-block">
                                ${product.brand ? `<div class="mb-2"><small class="text-dark"><strong>Бренд:</strong> ${product.brand}</small></div>` : ''}
                                ${product.sku ? `<div class="mb-2"><small class="text-dark"><strong>Артикул:</strong> ${product.sku}</small></div>` : ''}
                                ${product.standard ? `<div class="mb-2"><small class="text-dark"><strong>Стандарт:</strong> ${product.standard}</small></div>` : ''}
                                ${product.material ? `<div class="mb-2"><small class="text-dark"><strong>Материал:</strong> ${product.material}</small></div>` : ''}
                                ${product.application ? `<div class="mb-2"><small class="text-dark"><strong>Применение:</strong> ${product.application}</small></div>` : ''}
                                ${product.analogs ? `<div class="mb-2"><small class="text-dark"><strong>Аналоги:</strong> ${product.analogs}</small></div>` : ''}
                            </div>
                            
                            <!-- Mobile/Tablet view - collapsible -->
                            <div class="d-md-none">
                                <div class="accordion accordion-flush" id="productSpecs${product.id}">
                                    <div class="accordion-item">
                                        <h2 class="accordion-header">
                                            <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#productSpecsCollapse${product.id}" aria-expanded="false" aria-controls="productSpecsCollapse${product.id}">
                                                <i class="bi bi-gear-fill me-2"></i>
                                                <small>Характеристики</small>
                                            </button>
                                        </h2>
                                        <div id="productSpecsCollapse${product.id}" class="accordion-collapse collapse" aria-labelledby="productSpecsHeading${product.id}" data-bs-parent="#productSpecs${product.id}">
                                            <div class="accordion-body p-2">
                                                <div class="specs-list">
                                                    ${product.brand ? `<div class="spec-item"><span class="spec-label">Бренд:</span><span class="spec-value">${product.brand}</span></div>` : ''}
                                                    ${product.sku ? `<div class="spec-item"><span class="spec-label">Артикул:</span><span class="spec-value">${product.sku}</span></div>` : ''}
                                                    ${product.standard ? `<div class="spec-item"><span class="spec-label">Стандарт:</span><span class="spec-value">${product.standard}</span></div>` : ''}
                                                    ${product.material ? `<div class="spec-item"><span class="spec-label">Материал:</span><span class="spec-value">${product.material}</span></div>` : ''}
                                                    ${product.application ? `<div class="spec-item"><span class="spec-label">Применение:</span><span class="spec-value">${product.application}</span></div>` : ''}
                                                    ${product.analogs ? `<div class="spec-item"><span class="spec-label">Аналоги:</span><span class="spec-value">${product.analogs}</span></div>` : ''}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mt-auto">
                            <div class="d-grid gap-2">
                                <a href="/product/${product.id}" class="btn btn-outline-primary" onclick="event.stopPropagation();">
                                    <i class="bi bi-eye me-2"></i>Подробнее
                                </a>
                                <button class="btn btn-primary add-to-cart" 
                                        data-product-id="${product.id}" 
                                        data-product-name="${product.name}"
                                        onclick="event.stopPropagation();">
                                    <i class="bi bi-cart-plus me-2"></i>В корзину
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');

        console.log('Generated HTML length:', productsHTML.length);
        productsContainer.innerHTML = productsHTML;

        // Re-bind add to cart events
        this.bindAddToCartEvents();
        
        // Bind clickable card events
        this.bindClickableCardEvents();
    }

    renderCategories() {
        const categoriesContainer = document.getElementById('categories-container');
        if (!categoriesContainer) return;

        categoriesContainer.innerHTML = `
            <button class="btn category-filter ${this.currentCategory === 'all' ? 'btn-secondary' : 'btn-outline-secondary'}" 
                    data-category="all">
                Показать все
            </button>
            ${this.categories.map(category => `
                <button class="btn category-filter ${category.id === this.currentCategory ? 'btn-secondary' : 'btn-outline-secondary'}" 
                        data-category="${category.id}">
                    ${category.name}
                </button>
            `).join('')}
        `;

        // Bind category filter events
        this.bindCategoryEvents();
    }

    bindEvents() {
        // Search functionality
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.searchQuery = e.target.value;
                // Reset category filter when searching to show results from all categories
                if (this.searchQuery && this.currentCategory !== 'all') {
                    this.currentCategory = 'all';
                    this.renderCategories();
                }
                this.renderProducts();
            });
        }

        // Clear search button (if exists)
        const clearSearchBtn = document.getElementById('clear-search');
        if (clearSearchBtn) {
            clearSearchBtn.addEventListener('click', () => {
                this.clearSearch();
            });
        }

        // Sort functionality
        const sortSelect = document.getElementById('sort-select');
        if (sortSelect) {
            sortSelect.addEventListener('change', (e) => {
                this.sortProducts(e.target.value);
            });
        }

        // Cart events
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('add-to-cart')) {
                this.addToCart(e.target);
            } else if (e.target.classList.contains('remove-from-cart')) {
                this.removeFromCart(e.target);
            } else if (e.target.classList.contains('quantity-btn')) {
                this.updateQuantity(e.target);
            }
        });

        // Quantity input events
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('quantity-input')) {
                this.updateQuantityFromInput(e.target);
            }
        });
    }

    bindAddToCartEvents() {
        document.querySelectorAll('.add-to-cart').forEach(button => {
            button.addEventListener('click', (e) => {
                this.addToCart(e.target);
            });
        });
    }

    bindCategoryEvents() {
        document.querySelectorAll('.category-filter').forEach(button => {
            button.addEventListener('click', (e) => {
                this.currentCategory = e.target.dataset.category;
                this.renderProducts();
                this.renderCategories();
            });
        });
    }

    handleURLParams() {
        // Handle URL parameters for initial filtering
        const urlParams = new URLSearchParams(window.location.search);
        const category = urlParams.get('category');
        
        if (category) {
            // Check if category exists in our categories list
            const categoryExists = this.categories.some(cat => cat.id === category);
            if (categoryExists) {
                this.currentCategory = category;
                // Re-render after products and categories are loaded
                setTimeout(() => {
                    this.renderProducts();
                    this.renderCategories();
                }, 100);
            }
        }
    }

    bindClickableCardEvents() {
        document.querySelectorAll('.clickable-card').forEach(card => {
            card.addEventListener('click', (e) => {
                // Don't trigger if clicking on buttons or links
                if (e.target.closest('button') || e.target.closest('a')) {
                    return;
                }
                
                const productId = card.dataset.productId;
                if (productId) {
                    window.location.href = `/product/${productId}`;
                }
            });
            
            // Add hover effects
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-5px)';
                card.style.boxShadow = '0 8px 25px rgba(0,0,0,0.15)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0)';
                card.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
            });
        });
    }

    addToCart(button) {
        const productId = button.dataset.productId;
        const productName = button.dataset.productName;
        
        const existingItem = this.cart.find(item => item.id === productId);
        
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            this.cart.push({
                id: productId,
                name: productName,
                quantity: 1
            });
        }
        
        this.saveCart();
        this.updateCartCount();
        
        // Show success message
        button.textContent = 'Добавлено!';
        button.classList.remove('btn-primary');
        button.classList.add('btn-success');
        
        setTimeout(() => {
            button.textContent = 'В корзину';
            button.classList.remove('btn-success');
            button.classList.add('btn-primary');
        }, 1000);
    }

    removeFromCart(button) {
        const productId = button.dataset.productId;
        this.cart = this.cart.filter(item => item.id !== productId);
        this.saveCart();
        this.updateCartCount();
        this.updateCartDisplay();
    }

    updateQuantity(button) {
        const productId = button.dataset.productId;
        const item = this.cart.find(item => item.id === productId);
        
        if (item) {
            if (button.classList.contains('quantity-plus')) {
                item.quantity += 1;
            } else if (button.classList.contains('quantity-minus')) {
                if (item.quantity > 1) {
                    item.quantity -= 1;
                } else {
                    // Remove item if quantity becomes 0
                    this.cart = this.cart.filter(cartItem => cartItem.id !== productId);
                }
            }
            
            this.saveCart();
            this.updateCartCount();
            this.updateCartDisplay();
        }
    }

    updateQuantityFromInput(input) {
        const productId = input.dataset.productId;
        const newQuantity = parseInt(input.value) || 1;
        
        if (newQuantity < 1) {
            // Remove item if quantity is 0 or negative
            this.cart = this.cart.filter(item => item.id !== productId);
            this.saveCart();
            this.updateCartCount();
            this.updateCartDisplay();
            return;
        }
        
        const item = this.cart.find(item => item.id === productId);
        if (item) {
            item.quantity = newQuantity;
            this.saveCart();
            this.updateCartCount();
            this.updateCartDisplay();
        }
    }

    saveCart() {
        localStorage.setItem('cart', JSON.stringify(this.cart));
    }

    loadCart() {
        const savedCart = localStorage.getItem('cart');
        if (savedCart) {
            try {
                this.cart = JSON.parse(savedCart);
            } catch (e) {
                this.cart = [];
            }
        }
    }

    updateCartCount() {
        const totalItems = this.cart.reduce((sum, item) => sum + item.quantity, 0);
        
        const cartCount = document.getElementById('cart-count');
        
        if (cartCount) {
            cartCount.textContent = totalItems;
            // Show/hide badge
            if (totalItems > 0) {
                cartCount.classList.remove('d-none');
            } else {
                cartCount.classList.add('d-none');
            }
        }
        
        // Dispatch custom event to notify other parts of the app
        document.dispatchEvent(new CustomEvent('cartUpdated', {
            detail: {
                cart: this.cart,
                totalItems: totalItems
            }
        }));
    }

    updateCartDisplay() {
        const cartContainer = document.getElementById('cart-items');
        if (!cartContainer) return;

        if (this.cart.length === 0) {
            cartContainer.innerHTML = `
                <div class="text-center py-5">
                    <h4 class="text-muted">Корзина пуста</h4>
                    <p class="text-muted">Добавьте товары в корзину для оформления заявки</p>
                </div>
            `;
            return;
        }

        cartContainer.innerHTML = this.cart.map(item => `
            <div class="cart-item border-bottom py-3">
                <div class="row align-items-center">
                    <div class="col-md-4">
                        <h6 class="mb-0">${item.name}</h6>
                    </div>
                    <div class="col-md-3">
                        <div class="input-group">
                            <button class="btn btn-outline-secondary quantity-btn quantity-minus" 
                                    data-product-id="${item.id}">-</button>
                            <input type="number" class="form-control quantity-input text-center" 
                                   value="${item.quantity}" min="1" 
                                   data-product-id="${item.id}">
                            <button class="btn btn-outline-secondary quantity-btn quantity-plus" 
                                    data-product-id="${item.id}">+</button>
                        </div>
                    </div>
                    <div class="col-md-3 text-center">
                        <span class="badge bg-primary fs-6">${item.quantity} шт.</span>
                    </div>
                    <div class="col-md-2 text-end">
                        <button class="btn btn-outline-danger remove-from-cart" 
                                data-product-id="${item.id}">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');

        // Show minimum order warning
        const totalQuantity = this.cart.reduce((sum, item) => sum + item.quantity, 0);
        const warningElement = document.getElementById('min-order-warning');
        if (warningElement) {
            if (totalQuantity < this.minOrderQuantity) {
                warningElement.classList.remove('d-none');
                warningElement.innerHTML = `
                    <div class="alert alert-warning">
                        <i class="bi bi-exclamation-triangle"></i>
                        Минимальный заказ: ${this.minOrderQuantity} шт. 
                        В вашей корзине: ${totalQuantity} шт.
                    </div>
                `;
            } else {
                warningElement.classList.add('d-none');
            }
        }
        
        // Update cart summary in real-time
        this.updateCartSummaryRealTime();
    }

    updateCartSummaryRealTime() {
        const totalItems = this.cart.length;
        const totalQuantity = this.cart.reduce((sum, item) => sum + item.quantity, 0);
        
        // Update total items display
        const totalItemsElement = document.getElementById('total-items');
        if (totalItemsElement) {
            totalItemsElement.textContent = totalItems;
        }
        
        // Update total quantity display
        const totalQuantityElement = document.getElementById('total-quantity');
        if (totalQuantityElement) {
            totalQuantityElement.textContent = totalQuantity;
        }
        
        // Update submit button state
        const submitBtn = document.getElementById('submit-request-btn');
        if (submitBtn) {
            if (totalQuantity >= this.minOrderQuantity) {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Оформить заявку';
                submitBtn.classList.remove('btn-secondary');
                submitBtn.classList.add('btn-primary');
            } else {
                submitBtn.disabled = true;
                submitBtn.textContent = `Минимум ${this.minOrderQuantity} шт.`;
                submitBtn.classList.remove('btn-primary');
                submitBtn.classList.add('btn-secondary');
            }
        }
        
        // Update modal cart summary if modal is open
        const modal = document.getElementById('requestModal');
        if (modal && modal.classList.contains('show')) {
            this.populateModalCartSummary();
        }
    }

    populateModalCartSummary() {
        const modalSummary = document.getElementById('modal-cart-summary');
        if (!modalSummary) return;
        
        const cart = this.cart;
        if (cart.length === 0) {
            modalSummary.innerHTML = '<p class="text-muted">Корзина пуста</p>';
            return;
        }
        
        let summaryHTML = '';
        cart.forEach(item => {
            summaryHTML += `
                <div class="d-flex justify-content-between align-items-center mb-2">
                    <span>${item.name}</span>
                    <span class="badge bg-primary">${item.quantity} шт.</span>
                </div>
            `;
        });
        
        const totalQuantity = cart.reduce((sum, item) => sum + item.quantity, 0);
        summaryHTML += `
            <hr>
            <div class="d-flex justify-content-between align-items-center">
                <strong>Итого:</strong>
                <strong class="text-primary">${totalQuantity} шт.</strong>
            </div>
        `;
        
        modalSummary.innerHTML = summaryHTML;
    }

    sortProducts(sortBy) {
        switch (sortBy) {
            case 'name-asc':
                this.products.sort((a, b) => a.name.localeCompare(b.name));
                break;
            case 'name-desc':
                this.products.sort((a, b) => b.name.localeCompare(a.name));
                break;
            case 'category':
                this.products.sort((a, b) => a.category.localeCompare(b.category));
                break;
            default:
                // Default order (as in CSV)
                break;
        }
        this.renderProducts();
    }

    initializeAnimations() {
        // Intersection Observer for fade-in animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, observerOptions);

        // Observe all animated elements
        document.querySelectorAll('.fade-in, .fade-in-left, .fade-in-right, .scale-in').forEach(el => {
            observer.observe(el);
        });
    }

    // Facade fastener section functionality removed - now it's just a link to catalog

    clearSearch() {
        this.searchQuery = '';
        this.currentCategory = 'all';
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.value = '';
        }
        this.renderProducts();
        this.renderCategories();
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
    
    // Initialize facade fastener section if on homepage
    // Facade fastener initialization removed - now it's just a link to catalog
    
    // Initialize cart display if on cart page
    if (window.location.pathname === '/cart') {
        window.app.updateCartDisplay();
    }
    
    // Принудительное применение стилей для модальных окон на мобильных
    applyMobileModalStyles();
});

// Функция для принудительного применения стилей модальных окон на мобильных
function applyMobileModalStyles() {
    // Проверяем, что мы на мобильном устройстве
    const isMobile = window.innerWidth <= 768;
    
    if (isMobile) {
        // Применяем стили ко всем модальным окнам
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.addEventListener('show.bs.modal', function() {
                const dialog = this.querySelector('.modal-dialog');
                if (dialog) {
                    // Принудительно применяем стили
                    dialog.style.margin = '0.5rem';
                    dialog.style.maxWidth = 'calc(100vw - 1rem)';
                    dialog.style.width = 'calc(100vw - 1rem)';
                    
                    // Добавляем класс для центрирования
                    dialog.classList.add('modal-dialog-centered');
                    
                    // Принудительно обновляем стили через CSS
                    dialog.style.setProperty('margin', '0.5rem', 'important');
                    dialog.style.setProperty('max-width', 'calc(100vw - 1rem)', 'important');
                    dialog.style.setProperty('width', 'calc(100vw - 1rem)', 'important');
                }
            });
        });
        
        // Также применяем стили при изменении размера окна
        window.addEventListener('resize', function() {
            if (window.innerWidth <= 768) {
                const dialogs = document.querySelectorAll('.modal-dialog');
                dialogs.forEach(dialog => {
                    dialog.style.setProperty('margin', '0.5rem', 'important');
                    dialog.style.setProperty('max-width', 'calc(100vw - 1rem)', 'important');
                    dialog.style.setProperty('width', 'calc(100vw - 1rem)', 'important');
                });
            }
        });
        
        // Применяем стили к существующим модальным окнам
        const dialogs = document.querySelectorAll('.modal-dialog');
        dialogs.forEach(dialog => {
            dialog.style.setProperty('margin', '0.5rem', 'important');
            dialog.style.setProperty('max-width', 'calc(100vw - 1rem)', 'important');
            dialog.style.setProperty('width', 'calc(100vw - 1rem)', 'important');
        });
    }
}

// Дополнительная функция для принудительного обновления стилей
function forceUpdateModalStyles() {
    const dialogs = document.querySelectorAll('.modal-dialog');
    dialogs.forEach(dialog => {
        if (window.innerWidth <= 768) {
            dialog.style.setProperty('margin', '0.5rem', 'important');
            dialog.style.setProperty('max-width', 'calc(100vw - 1rem)', 'important');
            dialog.style.setProperty('width', 'calc(100vw - 1rem)', 'important');
        } else if (window.innerWidth <= 576) {
            dialog.style.setProperty('margin', '0.25rem', 'important');
            dialog.style.setProperty('max-width', 'calc(100vw - 0.5rem)', 'important');
            dialog.style.setProperty('width', 'calc(100vw - 0.5rem)', 'important');
        }
    });
}

// Обновляем стили при загрузке страницы и изменении размера
window.addEventListener('load', forceUpdateModalStyles);
window.addEventListener('resize', forceUpdateModalStyles);


