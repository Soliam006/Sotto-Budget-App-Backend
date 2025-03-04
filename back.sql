-- Insertar datos en la tabla 'user'
INSERT INTO user (id, username, email, password, role, language_preference, is_deleted)
VALUES
    (1, 'Soliam', 'test@test.com', '$2b$12$nCB79l3ZRFkV5MJWMr8v6.SsSLfNo9nyR5Kv3Idn7od5NXFVH3RMS', 'ADMIN', 'es', 0),
    (2, 'xin', 'xin@email.com', '$2b$12$mzvmfyk6aTx8k./r9Dwxt.4fZZklMP0ddBlIoOanzYM0thkWUxLGW', 'CLIENT', 'es', 0),
    (12, 'cliente_demo', 'cliente@example.com', '$2b$12$hashedpasswordexample', 'CLIENT', 'es', 0);

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