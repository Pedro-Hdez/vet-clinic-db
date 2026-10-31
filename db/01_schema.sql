-- Esquema de la clínica veterinaria.
-- El orden importa: una tabla debe existir antes de que otra haga referencia a ella.

-- owner_id es una llave sustituta. El correo sigue sin poder repetirse: UNIQUE.
CREATE TABLE owners (
    owner_id integer      PRIMARY KEY,
    email    varchar(255) NOT NULL UNIQUE,
    phone    varchar(20)  NOT NULL
);

-- owners (1..1) — pets (1..N): NOT NULL en la FK da el "exactamente un dueño".
-- El mínimo de 1 mascota por dueño no se puede forzar con una FK: es un supuesto documentado.
CREATE TABLE pets (
    pet_id   integer     PRIMARY KEY,
    name     varchar(50) NOT NULL,
    species  varchar(20) NOT NULL,
    owner_id integer     NOT NULL REFERENCES owners (owner_id)
);

-- pets (1..1) — visits (0..N): una mascota puede no tener consultas (Toby).
CREATE TABLE visits (
    visit_id   integer     PRIMARY KEY,
    visit_date date        NOT NULL,
    reason     varchar(50) NOT NULL,
    pet_id     integer     NOT NULL REFERENCES pets (pet_id)
);

CREATE TABLE vaccines (
    vaccine_id varchar(10)  PRIMARY KEY,
    name       varchar(50)  NOT NULL,
    price      numeric(6,2) NOT NULL CHECK (price >= 0)
);

-- Tabla de unión: la llave primaria es compuesta y cada una de sus columnas es FK.
-- visits (1..1) — visit_vaccine (0..N): la consulta 502 no tiene vacunas.
-- vaccines (1..1) — visit_vaccine (0..N): la leptospirosis no se ha aplicado.
CREATE TABLE visit_vaccine (
    visit_id   integer     NOT NULL REFERENCES visits (visit_id),
    vaccine_id varchar(10) NOT NULL REFERENCES vaccines (vaccine_id),
    dose       varchar(20) NOT NULL,
    PRIMARY KEY (visit_id, vaccine_id)
);
