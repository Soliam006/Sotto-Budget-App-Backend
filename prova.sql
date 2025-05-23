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
    (1, 1, 'Materials', 'Compra de materiales eléctricos', 1500.00, '2025-05-16 10:00:00', 'Approved', NOW(), NOW()),
    (2, 1, 'Labour', 'Pago a trabajadores', 2000.00, '2025-05-17 10:00:00', 'Pending', NOW(), NOW()),
    (3, 1, 'Transport', 'Gastos de transporte', 500.00, '2025-05-18 10:00:00', 'Approved', NOW(), NOW()),
    (4, 1, 'Others', 'Gastos varios', 300.00, '2025-05-19 10:00:00', 'Pending', NOW(), NOW()),
    (5, 1, 'Materials', 'Compra de herramientas', 1200.00, '2025-05-20 10:00:00', 'Approved', NOW(), NOW()),
    (6, 1, 'Labour', 'Pago a subcontratistas', 2500.00, '2025-05-21 10:00:00', 'Pending', NOW(), NOW()),
    (7, 1, 'Transport', 'Gastos de envío', 800.00, '2025-05-22 10:00:00', 'Approved', NOW(), NOW()),
    (8, 1, 'Others', 'Gastos imprevistos', 400.00, '2025-05-23 10:00:00', 'Pending', NOW(), NOW());



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


-- Insertar datos en la tabla 'tasks'
INSERT INTO task (id, project_id, worker_id, admin_id, title, description, status,  created_at, updated_at, due_date)
VALUES
    (1, 1, 1, 1, 'Instalación eléctrica', 'Realizar la instalación eléctrica del proyecto', 'In_Progress', NOW(), NOW(), '2025-05-25 10:00:00'),
    (2, 1, 1, 1, 'Revisión de seguridad', 'Revisar la seguridad de las instalaciones eléctricas', 'TODO', NOW(), NOW(), '2025-05-26 10:00:00'),
    (3, 1, 1, 1, 'Entrega de materiales', 'Entregar los materiales necesarios para el proyecto', 'DONE', NOW(), NOW(), '2025-05-27 10:00:00'),
    (4, 1, 1, 1, 'Informe final', 'Preparar el informe final del proyecto', 'TODO', NOW(), NOW(), '2025-05-28 10:00:00');

-- Insertar datos en la tabla 'inventoryitem'
INSERT INTO inventoryitem (id, name, category, total, used, remaining, unit, unit_cost, supplier, status, project_id)
VALUES
    (1, 'Cable eléctrico', 'Materials', 100, 20, 80, 'metros', 0.50, 'BricoMart', 'PENDING', 1),
    (2, 'Interruptor', 'Materials', 50, 10, 40, 'uds', 2.00, 'Sabadell', 'In_Budget', 1),
    (3, 'Bombilla LED', 'Materials', 200, 50, 150, 'uds', 1.00, 'Sabadell', 'Installed', 1),
    (4, 'Destornillador', 'Products', 30, 5, 25, 'uds', 3.00, 'BricoMart', 'Installed', 1),
    (5, 'Taladro eléctrico', 'Products', 10, 2, 8, 'uds', 50.00, 'ObraMat', 'Pending', 1),
    (6, 'Escalera', 'Products', 5, 1, 4, 'uds', 100.00, 'ObraMat', 'Installed', 1),
    (7, 'Guantes de seguridad', 'Products', 100, 20, 80, 'pares', 2.50, 'BricoMart', 'In_Budget', 1),
    (8, 'Casco de seguridad', 'Products', 50, 10, 40, 'uds', 15.00, 'BricoMart', 'Pending', 1);
