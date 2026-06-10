import argparse
import json
from movie.service import MovieReviewService
from movie.models import Movie

def build_service() -> MovieReviewService:
    svc = MovieReviewService()

    path = "data/movies_50.json"

    with open(path, "r", encoding="utf-8") as f:
        raw_movies = json.load(f)

    for item in raw_movies:
        movie = Movie.from_dict(item)
        svc.add_movie(movie)

    return svc

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
    for m in movies:
        print(m.short_info())

def main():
    parser = argparse.ArgumentParser(description="Movie Review Analytics CLI")
    subparsers = parser.add_subparsers(dest="command")

    find_parser = subparsers.add_parser("find", help="Поиск фильмов")
    find_parser.add_argument("--genre", type=str, help="Жанр фильма")
    find_parser.add_argument("--year-from", type=int, dest="year_from")
    find_parser.add_argument("--year-to", type=int, dest="year_to")
    find_parser.add_argument("--min-rating", type=float, dest="min_rating")
    find_parser.add_argument("--title", type=str, help="Подстрока названия")

    args = parser.parse_args()
    svc = build_service()

    if args.command == "find":
        cmd_find(args, svc)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()