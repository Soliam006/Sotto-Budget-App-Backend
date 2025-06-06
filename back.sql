-- ------------------------------------------------PROJECT 2------------------------------------------------------------
-- 1. Insertar usuarios necesarios (admin, worker, client)
INSERT INTO user (id, name, username, email, password, role, language_preference, is_deleted, phone, location, description, created_at)
VALUES
    (1, 'Admin Will', 'admin_will', 'admin@school.com', '$2b$12$nCB79l3ZRFkV5MJWMr8v6.SsSLfNo9nyR5Kv3Idn7od5NXFVH3RMS', 'ADMIN', 'es', 0, '1234567890', 'Madrid', 'Administrador del proyecto', NOW()),
    (2, 'Construction Manager', 'const_manager', 'manager@school.com', '$2b$12$nCB79l3ZRFkV5MJWMr8v6.SsSLfNo9nyR5Kv3Idn7od5NXFVH3RMS', 'WORKER', 'es', 0, '2345678901', 'Madrid', 'Gerente de construcción', NOW()),
    (3, 'Architect', 'project_architect', 'architect@school.com', '$2b$12$nCB79l3ZRFkV5MJWMr8v6.SsSLfNo9nyR5Kv3Idn7od5NXFVH3RMS', 'WORKER', 'es', 0, '3456789012', 'Madrid', 'Arquitecto principal', NOW()),
    (4, 'School District', 'school_client', 'client@school.com', '$2b$12$nCB79l3ZRFkV5MJWMr8v6.SsSLfNo9nyR5Kv3Idn7od5NXFVH3RMS', 'CLIENT', 'es', 0, '4567890123', 'Madrid', 'Distrito escolar', NOW()),
    (5, 'International Client', 'international_client', 'client2@test.com', '$2b$12$nCB79l3ZRFkV5MJWMr8v6.SsSLfNo9nyR5Kv3Idn7od5NXFVH3RMS', 'CLIENT', 'es', 0, '5678901234', 'Sevilla', 'Cliente internacional', NOW());


-- Insertar registros en tablas específicas de roles
INSERT INTO admin (id, user_id, is_deleted) VALUES (1, 1, 0);
INSERT INTO worker (id, user_id, is_deleted, specialty) VALUES
                                                            (1, 2, 0, 'Construction Management'),
                                                            (2, 3, 0, 'Architecture');
INSERT INTO client (id, user_id, budget_limit, is_deleted) VALUES (1, 4, 1500000, 0);
INSERT INTO client (id, user_id, budget_limit, is_deleted) VALUES (2, 5, 2000000, 0);

-- 2. Crear el proyecto principal -----------------------------------------------------------
INSERT INTO project (id, title, description, admin_id, limit_budget, location, start_date, end_date, status, created_at, updated_at)
VALUES (
           1,
           'Eco-Friendly School Building',
           'Construction of a new eco-friendly elementary school with solar panels and rainwater harvesting',
           1,
           1200000,
           'Calle Educación 123, Madrid',
           '2025-05-01 00:00:00',
           '2026-06-01 00:00:00',
           'ACTIVE',
           NOW(),
           NOW()
       );

-- 3. Asociar clientes y equipo al proyecto
INSERT INTO projectclient (project_id, client_id, created_at) VALUES (1, 1, NOW());
-- El CLiente debe seguir al admin del proyecto
INSERT INTO follow (follower_id, following_id, status, created_at, updated_at) VALUES
    (4, 1, 'ACCEPTED', NOW(), NOW());

-- Worker debe seguir al admin del proyecto
INSERT INTO follow (follower_id, following_id, status, created_at, updated_at) VALUES
    (2, 1, 'ACCEPTED', NOW(), NOW()),
    (3, 1, 'ACCEPTED', NOW(), NOW());
-- Asociar trabajadores al proyecto con roles específicos
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
INSERT INTO expense (id, project_id, expense_date, category, description, amount, status, created_at, updated_at, title)
VALUES
    (1, 1, '2025-06-05 00:00:00', 'MATERIALS', 'Initial bamboo flooring purchase', 52500, 'APPROVED', NOW(), NOW(), 'Bamboo Flooring Purchase'),
    (2, 1, '2025-06-10 00:00:00', 'LABOUR', 'First week construction labor', 25000, 'APPROVED', NOW(), NOW(), 'Construction Labor Week 1'),
    (3, 1, '2025-06-12 00:00:00', 'PRODUCTS', 'Deposit for solar panels', 50000, 'PENDING', NOW(), NOW(), 'Solar Panels Deposit');

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
    (1, 1, 4, NULL, 'TASK_CREATED', 'Eco-Friendly School Building', 1,
     '2025-05-01 09:00:00', '{"user": "admin_will", "title": "Design Eco Features"}'),
    (2, 1, 4, NULL, 'TASK_COMPLETED', 'Eco-Friendly School Building', 0, '2025-05-28 17:30:00', '{"user": "project_architect", "title": "Design Eco Features"}'),
    (3, 1, 2, NULL, 'TASK_CREATED', 'Eco-Friendly School Building', 1, '2025-06-01 10:15:00', '{"user": "admin_will", "title": "Site Preparation"}'),
    (4, 1, 2, NULL, 'TASK_UPDATED', 'Eco-Friendly School Building', 0, '2025-06-02 12:00:00', '{"user": "const_manager", "title": "Site Preparation"}'),
    (5, 1, NULL, 1, 'EXPENSE_ADDED', 'Eco-Friendly School Building', 1, '2025-06-05 11:20:00', '{"amount": 52500, "category": "MATERIALS", "description": "Initial bamboo flooring purchase", "status": "APPROVED", "title": "Bamboo Flooring Purchase"}'),
    (6, 1, NULL, 2, 'EXPENSE_UPDATED', 'Eco-Friendly School Building', 1, '2025-06-05 12:00:00', '{"amount": 25000, "category": "LABOUR", "description": "First week construction labor", "status": "PENDING", "title": "Construction Labor Week 1"}'),
    (7, 1, NULL, 3, 'EXPENSE_UPDATED', 'Eco-Friendly School Building', 0, '2025-06-05 12:30:00', '{"amount": 50000, "category": "PRODUCTS", "description": "Deposit for solar panels", "status": "PENDING", "title": "Solar Panels Deposit"}');

