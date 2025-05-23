-- ------------------------------------------------PROJECT 2------------------------------------------------------------
-- 1. Insertar usuarios necesarios (admin, worker, client)
INSERT INTO user (id, name, username, email, password, role, language_preference, is_deleted, phone, location, description, created_at)
VALUES
    (1, 'Admin Will', 'admin_will', 'admin@school.com', '$2b$12$nCB79l3ZRFkV5MJWMr8v6.SsSLfNo9nyR5Kv3Idn7od5NXFVH3RMS', 'ADMIN', 'es', 0, '1234567890', 'Madrid', 'Administrador del proyecto', NOW()),
    (2, 'Construction Manager', 'const_manager', 'manager@school.com', '$2b$12$nCB79l3ZRFkV5MJWMr8v6.SsSLfNo9nyR5Kv3Idn7od5NXFVH3RMS', 'WORKER', 'es', 0, '2345678901', 'Madrid', 'Gerente de construcción', NOW()),
    (3, 'Architect', 'project_architect', 'architect@school.com', '$2b$12$nCB79l3ZRFkV5MJWMr8v6.SsSLfNo9nyR5Kv3Idn7od5NXFVH3RMS', 'WORKER', 'es', 0, '3456789012', 'Madrid', 'Arquitecto principal', NOW()),
    (4, 'School District', 'school_client', 'client@school.com', '$2b$12$nCB79l3ZRFkV5MJWMr8v6.SsSLfNo9nyR5Kv3Idn7od5NXFVH3RMS', 'CLIENT', 'es', 0, '4567890123', 'Madrid', 'Distrito escolar', NOW());

-- Insertar registros en tablas específicas de roles
INSERT INTO admin (id, user_id, is_deleted) VALUES (1, 1, 0);
INSERT INTO worker (id, user_id, is_deleted, specialty) VALUES
                                                            (1, 2, 0, 'Construction Management'),
                                                            (2, 3, 0, 'Architecture');
INSERT INTO client (id, user_id, budget_limit, is_deleted) VALUES (1, 4, 1500000, 0);

-- 2. Crear el proyecto principal -----------------------------------------------------------
INSERT INTO project (id, title, description, admin_id, limit_budget, location, start_date, end_date, status, created_at, updated_at)
VALUES (
           1,
           'Eco-Friendly School Building',
           'Construction of a new eco-friendly elementary school with solar panels and rainwater harvesting',
           1,
           1200000,
           'Calle Educación 123, Madrid',
           '2025-06-01 00:00:00',
           '2026-06-01 00:00:00',
           'ACTIVE',
           NOW(),
           NOW()
       );

-- 3. Asociar clientes y equipo al proyecto
INSERT INTO projectclient (project_id, client_id, created_at) VALUES (1, 1, NOW());
INSERT INTO projectteamlink (project_id, worker_id, role) VALUES
                                                              (1, 1, 'Construction Manager'),
                                                              (1, 2, 'Lead Architect');

-- 4. Insertar items de inventario (presupuesto presentado al cliente)
INSERT INTO inventoryitem (id, name, category, total, used, remaining, unit, unit_cost, supplier, status, project_id)
VALUES
    (1, 'Solar Panels', 'PRODUCTS', 200, 0, 200, 'units', 500, 'SolarTech Inc.', 'IN_BUDGET', 1),
    (2, 'Rainwater Harvesting System', 'PRODUCTS', 1, 0, 1, 'system', 75000, 'EcoWater Systems', 'IN_BUDGET', 1),
    (3, 'Bamboo Flooring', 'MATERIALS', 1500, 0, 1500, 'sqm', 35, 'GreenMaterials Co.', 'IN_BUDGET', 1),
    (4, 'Architectural Design', 'SERVICES', 1, 0, 1, 'project', 50000, 'DesignStudio', 'IN_BUDGET', 1),
    (5, 'Construction Labor', 'LABOUR', 10000, 0, 10000, 'hours', 25, 'BuildRight Workers', 'IN_BUDGET', 1);

-- 5. Insertar gastos reales (solo visibles para admin)
INSERT INTO expense (id, project_id, expense_date, category, description, amount, status, created_at, updated_at)
VALUES
    (1, 1, '2025-06-05 00:00:00', 'MATERIALS', 'Initial bamboo flooring purchase', 52500, 'APPROVED', NOW(), NOW()),
    (2, 1, '2025-06-10 00:00:00', 'LABOUR', 'First week construction labor', 25000, 'APPROVED', NOW(), NOW()),
    (3, 1, '2025-06-12 00:00:00', 'PRODUCTS', 'Deposit for solar panels', 50000, 'PENDING', NOW(), NOW());

-- Asociar gastos al proyecto (con información adicional)
INSERT INTO projectexpenselink (project_id, expense_id, approved_by, notes, updated_at)
VALUES
    (1, 1, 'admin_will', 'Initial materials order for first phase', NOW()),
    (1, 2, 'admin_will', 'First week payroll', NOW()),
    (1, 3, NULL, 'Waiting for supplier confirmation', NOW());

-- 6. Crear tareas del proyecto
INSERT INTO task (id, project_id, admin_id, worker_id, title, description, status, created_at, updated_at, due_date)
VALUES
    (1, 1, 1, 2, 'Finalize Architectural Plans', 'Complete all architectural drawings and get approvals', 'TODO', NOW(), NOW(), '2025-06-15 00:00:00'),
    (2, 1, 1, 1, 'Site Preparation', 'Clear and prepare construction site', 'IN_PROGRESS', NOW(), NOW(), '2025-06-20 00:00:00'),
    (3, 1, 1, 1, 'Foundation Work', 'Pour concrete foundation', 'TODO', NOW(), NOW(), '2025-06-25 00:00:00'),
    (4, 1, 1, 2, 'Design Eco Features', 'Design solar panel and rainwater system integration', 'DONE', NOW(), NOW(), '2025-05-30 00:00:00');

-- 7. Registrar actividades/historial
INSERT INTO activity (id, project_id, task_id, expense_id, activity_type, title_project, is_read, created_at, metadatas)
VALUES
    (1, 1, 4, NULL, 'TASK_CREATED', 'Eco-Friendly School Building', 1, '2025-05-01 09:00:00', '{"user": "admin_will"}'),
    (2, 1, 4, NULL, 'TASK_COMPLETED', 'Eco-Friendly School Building', 0, '2025-05-28 17:30:00', '{"user": "project_architect"}'),
    (3, 1, 2, NULL, 'TASK_CREATED', 'Eco-Friendly School Building', 1, '2025-06-01 10:15:00', '{"user": "admin_will"}'),
    (4, 1, NULL, 1, 'EXPENSE_ADDED', 'Eco-Friendly School Building', 1, '2025-06-05 11:20:00', '{"amount": 52500}'),
    (5, 1, NULL, 1, 'EXPENSE_APPROVED', 'Eco-Friendly School Building', 0, '2025-06-05 14:30:00', '{"approved_by": "admin_will"}');