SET search_path TO movie;

CREATE TABLE IF NOT EXISTS movies (
    id              SERIAL PRIMARY KEY,
    title           VARCHAR(500)    NOT NULL,
    release_year    SMALLINT        NOT NULL,
    genres          TEXT[]          DEFAULT '{}',
    duration        INT,
    country         VARCHAR(100),
    description     TEXT,
    ratings         REAL[]          DEFAULT '{}',
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(100)    NOT NULL UNIQUE,
    email           VARCHAR(255)    NOT NULL UNIQUE,
    password_hash   TEXT            NOT NULL DEFAULT '',
    role            SMALLINT        NOT NULL DEFAULT 1,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    review_count    INT             NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT now(),
    last_login_at   TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS reviews (
    id          SERIAL PRIMARY KEY,
    movie_id    INT         NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
    user_id     INT         NOT NULL REFERENCES users(id)  ON DELETE CASCADE,
    rating      SMALLINT    NOT NULL CHECK (rating BETWEEN 1 AND 10),
    status      SMALLINT    NOT NULL DEFAULT 1,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);