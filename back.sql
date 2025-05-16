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
INSERT INTO project (id,title, description, limit_budget, location, start_date, end_date, status, created_at, admin_id, updated_at)
VALUES
    (1,'Proyecto Ejemplo', 'Descripción del proyecto de ejemplo', 10000, 'Madrid',
     '2025-05-15 11:25:23', '2025-05-20 11:25:23', 'Active', NOW(), 1, NOW());

-- Insertar datos en la tabla 'Expense'
INSERT INTO expense (id, project_id, category, description, amount, expense_date, status, created_at, updated_at)
VALUES
    (1, 1, 'Materiales', 'Compra de materiales eléctricos', 1500.00, '2025-05-16 10:00:00', 'Approved', NOW(), NOW()),
    (2, 1, 'Mano de obra', 'Pago a trabajadores', 2000.00, '2025-05-17 10:00:00', 'Pending', NOW(), NOW()),
    (3, 1, 'Transporte', 'Gastos de transporte', 500.00, '2025-05-18 10:00:00', 'Approved', NOW(), NOW()),
    (4, 1, 'Otros', 'Gastos varios', 300.00, '2025-05-19 10:00:00', 'Pending', NOW(), NOW()),
    (5, 1, 'Materiales', 'Compra de herramientas', 1200.00, '2025-05-20 10:00:00', 'Approved', NOW(), NOW()),
    (6, 1, 'Mano de obra', 'Pago a subcontratistas', 2500.00, '2025-05-21 10:00:00', 'Pending', NOW(), NOW()),
    (7, 1, 'Transporte', 'Gastos de envío', 800.00, '2025-05-22 10:00:00', 'Approved', NOW(), NOW()),
    (8, 1, 'Otros', 'Gastos imprevistos', 400.00, '2025-05-23 10:00:00', 'Pending', NOW(), NOW());



-- Insertar datos en la tabla 'projectexpenselink'
INSERT INTO projectexpenselink (project_id, expense_id, approved_by, notes, updated_at)
VALUES
    (1, 1, NULL, 'Aprobado por el administrador', NOW()),
    (1, 2, NULL, 'Aprobado por el administrador', NOW()),
    (1, 3, NULL, 'Aprobado por el administrador', NOW()),
    (1, 4, NULL, 'Aprobado por el administrador', NOW()),
    (1, 5, NULL, 'Aprobado por el administrador', NOW()),
    (1, 6, NULL, 'Aprobado por el administrador', NOW()),
    (1, 7, NULL, 'Aprobado por el administrador', NOW()),
    (1, 8, NULL, 'Aprobado por el administrador', NOW());
