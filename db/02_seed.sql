-- Datos del export de la clínica veterinaria.
-- El orden importa: primero las tablas a las que otras hacen referencia.

INSERT INTO owners (owner_id, email, phone) VALUES
    (1, 'carla@mail.com', '6621234567'),
    (2, 'jorge@mail.com', '6629876543'),
    (3, 'sofia@mail.com', '6625550101');

INSERT INTO pets (pet_id, name, species, owner_id) VALUES
    (1, 'Luna',  'perro', 1),
    (2, 'Michi', 'gato',  2),
    (3, 'Luna',  'gato',  2),
    (4, 'Rocky', 'perro', 3),
    -- Toby, recién adoptado: una mascota sin consultas.
    (5, 'Toby',  'perro', 3);

INSERT INTO visits (visit_id, visit_date, reason, pet_id) VALUES
    (501, '2026-03-02', 'Vacunación', 1),
    (502, '2026-03-15', 'Revisión',   2),
    (503, '2026-04-08', 'Vacunación', 3),
    (504, '2026-05-20', 'Vacunación', 1),
    (505, '2026-06-11', 'Vacunación', 4);

INSERT INTO vaccines (vaccine_id, name, price) VALUES
    ('V01', 'Rabia',         250),
    ('V02', 'Parvovirus',    380),
    ('V03', 'Triple felina', 420),
    ('V04', 'Moquillo',      350),
    -- Leptospirosis: una vacuna que no se ha aplicado.
    ('V05', 'Leptospirosis', 300);

-- La consulta 502 no aparece: fue una revisión sin vacunas.
INSERT INTO visit_vaccine (visit_id, vaccine_id, dose) VALUES
    (501, 'V01', '1.ª dosis'),
    (501, 'V02', '1.ª dosis'),
    (503, 'V01', '1.ª dosis'),
    (503, 'V03', '1.ª dosis'),
    (504, 'V04', '1.ª dosis'),
    (505, 'V01', 'refuerzo'),
    (505, 'V02', 'refuerzo'),
    (505, 'V04', 'refuerzo');
