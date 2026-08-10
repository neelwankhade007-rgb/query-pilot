INSERT INTO customers (name, email, city) VALUES
('Aarav Sharma', 'aarav@example.com', 'Nagpur'),
('Priya Mehta', 'priya@example.com', 'Mumbai'),
('Rohan Patil', 'rohan@example.com', 'Pune'),
('Ananya Deshmukh', 'ananya@example.com', 'Delhi'),
('Kabir Joshi', 'kabir@example.com', 'Bangalore');

INSERT INTO products (name, category, price) VALUES
('Laptop', 'Electronics', 65000.00),
('Mechanical Keyboard', 'Accessories', 4500.00),
('Wireless Mouse', 'Accessories', 1800.00),
('Monitor', 'Electronics', 22000.00),
('Headphones', 'Audio', 7500.00);

INSERT INTO orders (customer_id, product_id, quantity, order_date) VALUES
(1, 1, 1, '2026-07-01'),
(1, 3, 2, '2026-07-03'),
(2, 4, 1, '2026-07-05'),
(2, 5, 1, '2026-07-08'),
(3, 2, 2, '2026-07-10'),
(3, 3, 1, '2026-07-12'),
(4, 1, 1, '2026-07-15'),
(4, 5, 2, '2026-07-18'),
(5, 4, 1, '2026-07-20'),
(5, 2, 1, '2026-07-22');