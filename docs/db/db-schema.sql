-- User and Role Management
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    role ENUM(
        'ADMIN',
        'PRODUCER',
        'CUSTOMER'
    ) NOT NULL DEFAULT 'CUSTOMER',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE = InnoDB;

-- Producer Profiles
CREATE TABLE producer_profiles (
    user_id INT PRIMARY KEY,
    business_name VARCHAR(255) NOT NULL,
    business_address TEXT NOT NULL,
    postcode VARCHAR(10) NOT NULL,
    bio TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE = InnoDB;

-- Customer Profiles
CREATE TABLE customer_profiles (
    user_id INT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    delivery_address TEXT NOT NULL,
    postcode VARCHAR(10) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE = InnoDB;

-- Product Categories
CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
) ENGINE = InnoDB;

-- Products
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producer_id INT NOT NULL,
    category_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    unit VARCHAR(50) DEFAULT 'unit', -- e.g., 'dozen', 'kg'
    stock_quantity INT NOT NULL DEFAULT 0,
    allergen_info TEXT,
    is_organic BOOLEAN DEFAULT FALSE,
    is_available BOOLEAN DEFAULT TRUE,
    harvest_date DATE,
    best_before_date DATE,
    seasonal_start_month TINYINT, -- 1-12
    seasonal_end_month TINYINT, -- 1-12
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (producer_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories (id)
) ENGINE = InnoDB;

-- Orders
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    commission_total DECIMAL(10, 2) NOT NULL, -- Calculated 5%
    status ENUM(
        'PENDING',
        'CONFIRMED',
        'READY',
        'DELIVERED'
    ) DEFAULT 'PENDING',
    delivery_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES users (id)
) ENGINE = InnoDB;

-- Order Items
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price_at_sale DECIMAL(10, 2) NOT NULL,
    producer_payout DECIMAL(10, 2) NOT NULL, -- 95% of total
    network_commission DECIMAL(10, 2) NOT NULL, -- 5% of total
    FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products (id)
) ENGINE = InnoDB;

-- Surplus Produce Deals
CREATE TABLE surplus_deals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    discount_percentage DECIMAL(5, 2) NOT NULL,
    expiry_date DATETIME NOT NULL,
    deal_note VARCHAR(255),
    FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
) ENGINE = InnoDB;

-- Reviews
CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    order_id INT NOT NULL,
    rating TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES users (id),
    FOREIGN KEY (product_id) REFERENCES products (id),
    FOREIGN KEY (order_id) REFERENCES orders (id)
) ENGINE = InnoDB;