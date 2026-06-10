from .service import MovieReviewService
from .repository import MovieRepository, UserRepository, ReviewRepository


def load_service_from_db() -> MovieReviewService:
    """Создаёт экземпляр MovieReviewService и загружает в него все 
    фильмы, пользователей и отзывы из PostgreSQL."""
    svc = MovieReviewService()

    movie_repo = MovieRepository()
    user_repo = UserRepository()
    review_repo = ReviewRepository()

    for movie in movie_repo.get_all():
        svc.add_movie(movie)

    for user in user_repo.get_all():
        svc.add_user(user)

    for review in review_repo.get_all():
        svc.add_review(review)

    return svc