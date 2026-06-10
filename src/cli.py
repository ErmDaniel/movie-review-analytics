import argparse
import json
from movie.service import MovieReviewService
from movie.models import Movie

from movie.loaders import load_service_from_db
from movie.exceptions import ServiceIndexError

def build_service() -> MovieReviewService:
    """Создаёт сервис и загружает данные из PostgreSQL."""
    return load_service_from_db()

def print_movie(movie):
    print(f"[{movie.id}] {movie.short_info()}")
    if getattr(movie, "_genres", None):
        print(f"Genres: {', '.join(movie._genres)}")
    if getattr(movie, "_country", None):
        print(f"Country: {movie._country}")
    if getattr(movie, "_duration", None):
        print(f"Duration: {movie._duration} min")
    if getattr(movie, "_description", None):
        print(f"Description: {movie._description}")
    print()

def cmd_find(args, svc: MovieReviewService):
    movies = svc.find_movies(
        genre=args.genre,
        year_from=args.year_from,
        year_to=args.year_to,
        min_avg_rating=args.min_rating,
        title_contains=args.title,
    )
    if not movies:
        print("Фильмы не найдены.")
        return
    
    print(f"Найдено фильмов: {len(movies)}")
    for m in movies:
        print(m.short_info())

def cmd_movie(args, service):
    try:
        movie = service.get_movie(args.movie_id)
    except ServiceIndexError as e:
        print(f"Ошибка: {e}")
        return

    print_movie(movie)

def create_parser():
    parser = argparse.ArgumentParser(
        description="CLI для системы рецензирования и анализа фильмов"
    )

    subparsers = parser.add_subparsers(dest="command")

    find_parser = subparsers.add_parser(
        "find",
        help="Поиск фильмов по фильтрам",
    )
    find_parser.add_argument("--genre", type=str, help="Жанр фильма")
    find_parser.add_argument("--year-from", type=int, dest="year_from", help="Минимальный год выпуска")
    find_parser.add_argument("--year-to", type=int, dest="year_to", help="Максимальный год выпуска")
    find_parser.add_argument("--min-rating", type=float, dest="min_rating", help="Минимальная средняя оценка")
    find_parser.add_argument("--max-rating", type=float, dest="max_rating", help="Максимальная средняя оценка")
    find_parser.add_argument("--title", type=str, help="Подстрока в названии фильма")
    find_parser.set_defaults(func=cmd_find)

    movie_parser = subparsers.add_parser(
        "movie",
        help="Показать фильм по id",
    )
    movie_parser.add_argument("movie_id", type=int, help="ID фильма")
    movie_parser.set_defaults(func=cmd_movie)

    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        return

    service = build_service()
    args.func(args, service)

if __name__ == "__main__":
    main()