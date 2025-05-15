INSERT INTO user (id, name, username, email, password, role, language_preference, is_deleted, phone, location, description, created_at)
VALUES
    (1, 'will', 'will', 'test@test.com', '$2b$12$nCB79l3ZRFkV5MJWMr8v6.SsSLfNo9nyR5Kv3Idn7od5NXFVH3RMS', 'ADMIN', 'es', 0, '1234567890', 'Madrid', 'Administrador del sistema', NOW()),
    (2, 'client', 'client', 'test2@test.com', '$2b$12$nCB79l3ZRFkV5MJWMr8v6.SsSLfNo9nyR5Kv3Idn7od5NXFVH3RMS', 'CLIENT', 'es', 0, '2345678901', 'Barcelona', 'Cliente habitual', NOW()),
    (3, 'worker', 'worker', 'test3@test.com', '$2b$12$nCB79l3ZRFkV5MJWMr8v6.SsSLfNo9nyR5Kv3Idn7od5NXFVH3RMS', 'WORKER', 'es', 0, '3456789012', 'Valencia', 'Trabajador especializado', NOW()),
    (10, 'xin', 'xin', 'xin@email.com', '$2b$12$mzvmfyk6aTx8k./r9Dwxt.4fZZklMP0ddBlIoOanzYM0thkWUxLGW', 'CLIENT', 'es', 0, '4567890123', 'Sevilla', 'Cliente internacional', NOW()),
    (12, 'cliente_demo', 'cliente_demo', 'cliente@example.com', '$2b$12$hashedpasswordexample', 'CLIENT', 'es', 0, '5678901234', 'Bilbao', 'Cliente de demostración', NOW());
-- Insertar en la tabla 'client' vinculando usuarios con rol CLIENT
INSERT INTO client (user_id, budget_limit, is_deleted)
VALUES
    (2, 5000.00, 0),
    (12, 7000.00, 0);
-- Insertar rangos de disponibilidad en 'clientavailability'
INSERT INTO clientavailability (client_id, start_date, end_date, created_at)
VALUES
     (2, '2024-03-10 08:00:00', '2024-03-10 12:00:00', NOW()),
     (2, '2024-03-11 14:00:00', '2024-03-11 18:00:00', NOW()),
     (2, '2024-03-12 09:00:00', '2024-03-12 13:00:00', NOW());

-- Insertar datos en la tabla 'admin'
INSERT INTO admin (id, user_id, is_deleted)
VALUES
    (1, 1, 0);

-- Insertar datos en la tabla 'worker'
INSERT INTO worker (user_id, is_deleted, specialty)
VALUES
    (3, 0, 'Electricista');
-- Insertar un ejemplo de proyecto en la tabla 'project'
INSERT INTO project (title, description, limit_budget, location, start_date, end_date, status, created_at, admin_id, updated_at)
VALUES
    ('Proyecto Ejemplo', 'Descripción del proyecto de ejemplo', 10000, 'Madrid',
     '2025-05-15 11:25:23', '2025-05-20 11:25:23', 'Active', NOW(), 5, NOW());