from .decorators import sync_by_review_id
from .enums import ReviewStatus
from .exceptions import ServiceTypeError, ServiceIndexError, ServiceValidationError
from .models import Movie, Review, User


class MovieReviewService:
    def __init__(self) -> None:
        self._users: dict[int, User] = {}
        self._movies: dict[int, Movie] = {}
        self._reviews: dict[int, Review] = {}

    def add_user(self, user: User) -> None:
        if not isinstance(user, User):
            raise ServiceTypeError("Expected User instance")

        if user.id in self._users:
            raise ServiceIndexError(f"User with id={user.id} already exists")

        self._users[user.id] = user
        
    def has_user(self, user_id: int) -> bool:
        return user_id in self._users
    
    def get_user(self, user_id: int) -> User:
        if self.has_user(user_id):
            return self._users[user_id]
        else:
            raise ServiceIndexError(f"User with id={user_id} not found")
        
    def add_movie(self, movie: Movie) -> None:
        if not isinstance(movie, Movie):
            raise ServiceTypeError("Expected Movie instance")

        if movie.id in self._movies:
            raise ServiceIndexError(f"Movie with id={movie.id} already exists")

        self._movies[movie.id] = movie

    def has_movie(self, movie_id: int) -> bool:
        return movie_id in self._movies
        
    def get_movie(self, movie_id: int) -> Movie:
        if self.has_movie(movie_id):
            return self._movies[movie_id]
        else:
            raise ServiceIndexError(f"Movie with id={movie_id} not found")

    def add_review(self, review: Review) -> None:
        if not isinstance(review, Review):
            raise ServiceTypeError("Expected Review instance")

        if review.id in self._reviews:
            raise ServiceIndexError(f"Review with id={review.id} already exists")

        if not self.has_user(review.user_id):
            raise ServiceIndexError(f"User with id={review.user_id} not found")

        if not self.has_movie(review.movie_id):
            raise ServiceIndexError(f"Movie with id={review.movie_id} not found")

        self._reviews[review.id] = review
        self._recalculate_movie_rating(review.movie_id)
        self._recalculate_user_review_count(review.user_id)

    def has_review(self, review_id: int) -> bool:
        return review_id in self._reviews

    def get_review(self, review_id: int) -> Review:
        if self.has_review(review_id):
            return self._reviews[review_id]
        else:
            raise ServiceIndexError(f"Review with id={review_id} not found")

    def _recalculate_movie_rating(self, movie_id: int) -> None:
        movie = self.get_movie(movie_id)

        active_ratings = [
            review.rating 
            for review in self._reviews.values()
            if review.movie_id == movie_id and review.is_active
        ]

        movie.set_rating(active_ratings)

    def _recalculate_user_review_count(self, user_id: int) -> None:
        user = self.get_user(user)

        active_review_count = sum(
            1
            for review in self._reviews.values()
            if review.user_id == user_id and review.is_active 
        )

        user.set_review_count(active_review_count)

    def get_movie_reviews(self, movie_id, *, with_inactive: bool = False) -> list[Review]:
        self.get_movie(movie_id)

        if with_inactive:
            reviews = [
                review
                for review in self._reviews.values()
                if review.movie_id == movie_id
            ]
        else:
            reviews = [
                review
                for review in self._reviews.values()
                if review.movie_id == movie_id and review.is_active
            ]

        return sorted(reviews, key=lambda review: review.created_at, reverse=True)

    def get_user_reviews(self, user_id, *, with_inactive: bool = False) -> list[Review]:
        self.get_user(user_id)

        if with_inactive:
            reviews = [
                review
                for review in self._reviews.values()
                if review.user_id == user_id
            ]
        else:
            reviews = [
                review
                for review in self._reviews.values()
                if review.user_id == user_id and review.is_active
            ]

        return sorted(reviews, key=lambda review: review.created_at, reverse=True)

    @sync_by_review_id
    def hide_review(self, review_id: int) -> None:
        review = self.get_review(review_id)

        if review.status == ReviewStatus.DELETED:
            raise ServiceValidationError("Review is deleted and cannot be hidden")

        if review.status == ReviewStatus.HIDDEN:
            return

        review.hide()

    @sync_by_review_id
    def delete_review(self, review_id: int) -> None:
        review = self.get_review(review_id)

        if review.status == ReviewStatus.DELETED:
            return
        
        review.mark_deleted()

    def publish_review(self, review_id: int) -> None:
        review = self.get_review(review_id)

        if review.status == ReviewStatus.DELETED:
            raise ServiceValidationError("Review is deleted and cannot be published")
    
        if review.status == ReviewStatus.PUBLISHED:
            return
    
        review.publish()

    def update_review_rating(self, review_id: int, new_rating: int) -> None:
        review = self.get_review(review_id)
        
        if review.status == ReviewStatus.DELETED:
            raise ServiceValidationError("Review is deleted and cannot be changed") 
            
        review.change_rating(new_rating)