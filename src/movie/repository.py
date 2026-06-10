import psycopg2
from .models import Movie, User, Review
from .db import get_connection

class MovieRepository:

    def add(self, movie: Movie) -> int:
        """Сохраняет фильм и возвращает id, назначенный БД."""
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO movies
                        (title, release_year, genres, duration,
                         country, description, ratings, created_at, updated_at)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        movie._title,
                        movie._release_year,
                        movie._genres,        # psycopg2 умеет писать Python list как PostgreSQL ARRAY
                        movie._duration,
                        movie._country,
                        movie._description,
                        movie._ratings,
                        movie._created_at,
                        movie._updated_at,
                    ),
                )
                row = cur.fetchone()
            conn.commit()
        return row["id"]

    def get_by_id(self, movie_id: int) -> Movie | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM movies WHERE id = %s", (movie_id,))
                row = cur.fetchone()
        if row is None:
            return None
        return Movie.from_dict(dict(row))

    def get_all(self) -> list[Movie]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM movies ORDER BY id")
                rows = cur.fetchall()
        return [Movie.from_dict(dict(r)) for r in rows]

    def update(self, movie: Movie) -> None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE movies SET
                        title        = %s,
                        release_year = %s,
                        genres       = %s,
                        duration     = %s,
                        country      = %s,
                        description  = %s,
                        ratings      = %s,
                        updated_at   = %s
                    WHERE id = %s
                    """,
                    (
                        movie._title,
                        movie._release_year,
                        movie._genres,
                        movie._duration,
                        movie._country,
                        movie._description,
                        movie._ratings,
                        movie._updated_at,
                        movie._id,
                    ),
                )
            conn.commit()

    def delete(self, movie_id: int) -> None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM movies WHERE id = %s", (movie_id,))
            conn.commit()


class UserRepository:

    def add(self, user: User) -> int:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users
                        (username, email, password_hash, role, is_active,
                         review_count, created_at, updated_at, last_login_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        user._username,
                        user._email,
                        user._password_hash,
                        int(user._role),
                        user._is_active,
                        user._review_count,
                        user._created_at,
                        user._updated_at,
                        user._last_login_at,
                    ),
                )
                row = cur.fetchone()
            conn.commit()
        return row["id"]

    def get_by_id(self, user_id: int) -> User | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                row = cur.fetchone()
        if row is None:
            return None
        return User.from_dict(dict(row))

    def get_all(self) -> list[User]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users ORDER BY id")
                rows = cur.fetchall()
        return [User.from_dict(dict(r)) for r in rows]


class ReviewRepository:

    def add(self, review: Review) -> int:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO reviews
                        (movie_id, user_id, rating, status, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        review._movie_id,
                        review._user_id,
                        review._rating,
                        int(review._status),
                        review._created_at,
                        review._updated_at,
                    ),
                )
                row = cur.fetchone()
            conn.commit()
        return row["id"]

    def get_by_id(self, review_id: int) -> Review | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM reviews WHERE id = %s", (review_id,))
                row = cur.fetchone()
        if row is None:
            return None
        return Review.from_dict(dict(row))

    def get_by_movie(self, movie_id: int) -> list[Review]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM reviews WHERE movie_id = %s ORDER BY created_at DESC",
                    (movie_id,),
                )
                rows = cur.fetchall()
        return [Review.from_dict(dict(r)) for r in rows]

    def get_by_user(self, user_id: int) -> list[Review]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM reviews WHERE user_id = %s ORDER BY created_at DESC",
                    (user_id,),
                )
                rows = cur.fetchall()
        return [Review.from_dict(dict(r)) for r in rows]

    def update_status(self, review_id: int, status: int) -> None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE reviews SET status = %s, updated_at = now() WHERE id = %s",
                    (status, review_id),
                )
            conn.commit()

    def get_all(self) -> list[Review]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM reviews ORDER BY id")
                rows = cur.fetchall()

        return [Review.from_dict(dict(row)) for row in rows]