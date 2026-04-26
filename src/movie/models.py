from copy import deepcopy
from dataclasses import dataclass, field
from datetime import UTC, datetime

from .enums import ReviewStatus, UserRole
from .exceptions import PasswordError
from .security import password_hasher, VerifyMismatchError
from .decorators import (
    roolback_on_validating,
    validating_movie,
    validating_review,
    validating_user,
)

@dataclass(slots=True)
class Movie:
    _id: int
    _title: str
    _release_year: int
    _genres: list[str] = field(default_factory=list)
    _duration: int | None = None
    _country: str | None = None
    _description: str | None = None    

    _ratings: list[int | float] = field(default_factory=list)
    
    _created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    
    @validating_movie(v_title=True, v_release_year=True, v_genres=True)
    def __post_init__(self) -> None:
        pass

    @property
    def count_ratings(self) -> int:
        return len(self._ratings)

    @property
    def average_rating(self) -> float:
        return 0.0 if not self._ratings else sum(self._ratings) / self.count_ratings

    @roolback_on_validating
    @validating_movie(v_title=True)
    def set_title(self, new_title: str) -> None:
        self._title = new_title

    @roolback_on_validating
    @validating_movie(v_release_year=True)
    def set_release_year(self, new_release_year: int) -> None:
        self._release_year = new_release_year

    @roolback_on_validating
    @validating_movie(v_genres=True)
    def set_genres(self, new_genres: list[str]) -> None:
        self._genres = new_genres

    
    def add_genre(self, genre: str) -> None:
        genre = genre.strip()
        if genre and genre not in self._genres:
            self._genres.append(genre)
            self.touch()

    
    def remove_genre(self, genre: str) -> None:
        if genre in self._genres:
            self._genres.remove(genre)
            self.touch()

    
    def set_other_details(
        self,
        *,
        new_duration: int | None = None,
        new_country: str | None = None,
        new_description: str | None = None
    ):
        if isinstance(new_duration, int) and new_duration > 0:
            self._duration = new_duration
            self.touch()

        if isinstance(new_country, str) and new_country.strip():
            self._country = new_country
            self.touch()

        if isinstance(new_description, str) and new_description.strip():
            self._description = new_description
            self.touch()

    
    def set_rating(self, new_ratings: list[int | float]) -> None:
        self._ratings = new_ratings
        self.touch()

    def short_info(self) -> str:
        return f"{self._title} ({self._release_year}) - rating: {self.average_rating}"

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "title": self._title,
            "release_year": self._release_year,
            "genres": list(self._genres),
            "duration": self._duration,
            "country": self._country,
            "description": self._description,
            "ratings": list(self._ratings),
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Movie":
        return cls(
            _id=data["id"],
            _title=data["title"],
            _release_year=data["release_year"],
            _genres=list(data.get("genres", [])),
            _duration=data.get("duration"),
            _country=data.get("country"),
            _description=data.get("description"),
            _ratings=list(data.get("ratings", [])),
            _created_at=(
                datetime.fromisoformat(data["created_at"])
                if "created_at" in data and data["created_at"] is not None
                else datetime.now(UTC)
            ),
            _updated_at=(
                datetime.fromisoformat(data["updated_at"])
                if "updated_at" in data and data["updated_at"] is not None
                else datetime.now(UTC)
            ),
        )

    def _get_state(self):
        return deepcopy({
            "title": self._title,
            "release_year": self._release_year,
            "genres": self._genres
        })

    def _set_state(self, saved_state: dict):
        self._title = saved_state["title"]
        self._release_year = saved_state["release_year"]
        self._genres = saved_state["genres"]

    def touch(self) -> None:
        self._updated_at = datetime.now(UTC)
        

@dataclass(slots=True)
class User:
    _id: int
    
    _username: str
    _email: str
    _password_hash: str = field(default="", repr=False)

    _role: UserRole = UserRole.USER
    _is_active: bool = True

    _review_count: int = 0

    _created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _last_login_at: datetime | None = None

    @validating_user(v_username=True, v_email=True, v_role=True)
    def __post_init__(self) -> None:
        pass

    def set_password(self, raw_password: str) -> None:
        if len(raw_password) < 8:
            raise PasswordError("Password must be at least 8 characters long")
        self._password_hash = password_hasher.hash(raw_password)
        self.touch()

    def check_password(self, raw_password: str) -> bool:
        if not self.password_hash:
            return False
        try:
            return password_hasher.verify(self._password_hash, raw_password)
        except VerifyMismatchError:
            return False

    def change_password(self, old_password: str, new_password: str) -> None:
        if not self.check_password(old_password):
            raise PasswordError("Old password is incorrect")
        self.set_password(new_password)

    def _mark_login(self) -> None:
        self._last_login_at = datetime.utcnow()
        self.touch()

    def _deactivate(self) -> None:
        self._is_active = False
        self.touch()

    def _activate(self) -> None:
        self._is_active = True
        self.touch()

    def to_dict(self, include_sensitive: bool = False) -> dict:
        data = {
            "id": self._id,
            "username": self._username,
            "email": self._email,
            "role": int(self._role),
            "is_active": self._is_active,
            "review_count": self._review_count,
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat(),
            "last_login_at": (
                self._last_login_at.isoformat()
                if self._last_login_at is not None
                else None
            ),
        }

        if include_sensitive:
            data["password_hash"] = self._password_hash

        return data

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            _id=data["id"],
            _username=data["username"],
            _email=data["email"],
            _password_hash=data.get("password_hash", ""),
            _role=UserRole(data.get("role", UserRole.USER)),
            _is_active=data.get("is_active", True),
            _review_count=data.get("review_count", 0),
            _created_at=(
                datetime.fromisoformat(data["created_at"])
                if "created_at" in data and data["created_at"] is not None
                else datetime.now(UTC)
            ),
            _updated_at=(
                datetime.fromisoformat(data["updated_at"])
                if "updated_at" in data and data["updated_at"] is not None
                else datetime.now(UTC)
            ),
            _last_login_at=(
                datetime.fromisoformat(data["last_login_at"])
                if "last_login_at" in data and data["last_login_at"] is not None
                else None
            ),
        )
        
    def touch(self) -> None:
        self._updated_at = datetime.now(UTC)

@dataclass(slots=True)
class Review:
    _id: int
    _movie_id: int
    _user_id: int
    _rating: int

    _status: ReviewStatus = ReviewStatus.PUBLISHED

    _created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    MIN_RATING: int = field(default=1, init=False, repr=False)
    MAX_RATING: int = field(default=10, init=False, repr=False)

    @validating_review(v_links=True, v_rating=True, v_status=True)
    def __post_init__(self) -> None:
        pass

    @roolback_on_validating
    @validating_review(v_rating=True)
    def change_rating(self, new_rating: int) -> None:
        self._rating = new_rating

    def publish(self) -> None:
        self._status = ReviewStatus.PUBLISHED
        self.touch()

    def hide(self) -> None:
        self._status = ReviewStatus.HIDDEN
        self.touch()

    def mark_deleted(self) -> None:
        self._status = ReviewStatus.DELETED
        self.touch()

    def is_active(self) -> bool:
        return self._status == ReviewStatus.PUBLISHED

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "movie_id": self._movie_id,
            "user_id": self._user_id,
            "rating": self._rating,
            "status": int(self._status),
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Review":
        return cls(
            _id=data["id"],
            _movie_id=data["movie_id"],
            _user_id=data["user_id"],
            _rating=data["rating"],
            _status=ReviewStatus(data.get("status", 1)),
            _created_at=datetime.fromisoformat(data["created_at"])
            if "created_at" in data else datetime.now(UTC),
            _updated_at=datetime.fromisoformat(data["updated_at"])
            if "updated_at" in data else datetime.now(UTC),
        )

    def touch(self) -> None:
        self._updated_at = datetime.now(UTC)

    def _get_state(self):
        return deepcopy({
            "rating": self._rating,
        })

    def _set_state(self, saved_state: dict):
        self._rating = saved_state["rating"]