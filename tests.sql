-- Pruebas de la clínica veterinaria.
-- Cada comentario dice qué resultado esperar.

-- ---------------------------------------------------------------------
-- a) Preguntas de negocio
-- ---------------------------------------------------------------------

-- ¿Qué vacunas recibió cada mascota, y en qué consulta?
-- Esperado: 8 filas. La consulta 502 no aparece, porque no tuvo vacunas.
SELECT p.name AS mascota, o.email AS dueno, v.visit_date, va.name AS vacuna, vv.dose
FROM visit_vaccine vv
JOIN visits v    ON v.visit_id = vv.visit_id
JOIN pets p      ON p.pet_id = v.pet_id
JOIN owners o    ON o.owner_id = p.owner_id
JOIN vaccines va ON va.vaccine_id = vv.vaccine_id
ORDER BY v.visit_date, va.name;

-- ¿Cuántas consultas tiene cada mascota? Que aparezcan también las que no tienen.
-- Esperado: 5 filas. Toby tiene 0; LEFT JOIN lo conserva y un JOIN normal lo perdería.
SELECT p.pet_id, p.name, COUNT(v.visit_id) AS consultas
FROM pets p
LEFT JOIN visits v ON v.pet_id = p.pet_id
GROUP BY p.pet_id, p.name
ORDER BY p.pet_id;

-- ¿Qué vacunas no se han aplicado?
-- Esperado: 1 fila, Leptospirosis.
SELECT va.vaccine_id, va.name
FROM vaccines va
LEFT JOIN visit_vaccine vv ON vv.vaccine_id = va.vaccine_id
WHERE vv.vaccine_id IS NULL;

-- ---------------------------------------------------------------------
-- b) Intentos de romper las reglas
-- Cada instrucción debe producir un ERROR. psql lo muestra y sigue.
-- ---------------------------------------------------------------------

-- PRIMARY KEY: no puede haber dos mascotas con el mismo identificador.
-- Esperado: ERROR por llave duplicada.
INSERT INTO pets (pet_id, name, species, owner_id)
VALUES (1, 'Firulais', 'perro', 1);

-- UNIQUE: dos dueños no pueden tener el mismo correo.
-- Esperado: ERROR por llave duplicada.
INSERT INTO owners (owner_id, email, phone)
VALUES (4, 'carla@mail.com', '6620000000');

-- FOREIGN KEY: toda consulta es de una mascota registrada.
-- Esperado: ERROR por violar la llave foránea.
INSERT INTO visits (visit_id, visit_date, reason, pet_id)
VALUES (506, '2026-07-01', 'Revisión', 99);

-- NOT NULL: toda mascota tiene exactamente un dueño (el mínimo de 1 de la relación).
-- Esperado: ERROR por valor nulo.
INSERT INTO pets (pet_id, name, species, owner_id)
VALUES (6, 'Nala', 'gato', NULL);

-- CHECK: una vacuna no puede tener precio negativo.
-- Esperado: ERROR por violar la restricción check.
UPDATE vaccines SET price = -10 WHERE vaccine_id = 'V01';

-- FOREIGN KEY al borrar: no se puede borrar a un dueño que todavía tiene mascotas.
-- Esperado: ERROR por violar la llave foránea.
DELETE FROM owners WHERE owner_id = 1;

-- PRIMARY KEY compuesta: una vacuna no se repite dentro de una misma consulta.
-- Esperado: ERROR por llave duplicada.
INSERT INTO visit_vaccine (visit_id, vaccine_id, dose)
VALUES (501, 'V01', 'refuerzo');
