from functools import wraps
from collections.abc import Iterable
import re

from .exceptions import Validation_Error
from .enums import ReviewStatus, UserRole

def roolback_on_validating(func):
    """
    Декоратор для методов, изменяющих состояние экземпляра и проходящих валидацию.

    Перед вызовом исходного метода декоратор сохраняет текущее состояние объекта
    (через методы _get_state/_set_state). Если во время выполнения метода будет
    выброшено исключение Validation_Error, состояние экземпляра откатывается к
    сохранённому.

    При успешном выполнении метода (без Validation_Error) состояние не
    откатывается, и могут быть выполнены дополнительные действия после вызова
    исходной функции (например, обновление времени модификации через self.touch()).
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        saved_state = self._get_state()
        try:
            result = func(self, *args, **kwargs)
        except Validation_Error as e:
            print(f"Ошибка валидации: {e}")
            self._set_state(saved_state)
        else:
            self.touch()
            return result
        
    return wrapper

# ------------------------------------------------------------------------------------------------------------------------------------------------
    
def validating_movie(
    v_title: bool = False, 
    v_release_year: bool = False, 
    v_genres: bool = False
):
    """
    Создаёт декоратор для пост-валидации атрибутов объекта фильма.

    Сначала выполняется декорируемый метод, затем в зависимости от переданных
    флагов выполняется проверка выбранных атрибутов объекта.

    Args:
        v_title: Если True, проверяет, что ``self._title`` является непустой
            строкой и не состоит только из пробелов.
        v_release_year: Если True, проверяет, что ``self._release_year`` не
            меньше 1888 года.
        v_genres: Если True, проверяет, что ``self._genres`` — это итерируемый
            объект, не являющийся строкой, и что каждый жанр — непустая строка,
            не состоящая только из пробелов.

    Returns:
        Callable: Декоратор, оборачивающий метод экземпляра и выполняющий
        пост-валидацию после его выполнения.

    Raises:
        Validation_Error: Если включена проверка названия и ``self._title``
            некорректно.
        Validation_Error: Если включена проверка года релиза и
            ``self._release_year`` некорректен.
        Validation_Error: Если включена проверка жанров и ``self._genres`` имеет
            некорректную структуру или содержит некорректные значения жанров.
    """
    def outer(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            
            if v_title and (not isinstance(self._title, str) or not self._title.strip()):
                raise Validation_Error("Movie title is empty")

            if v_release_year and self._release_year < 1888:
                raise Validation_Error("Invalid release year")

            if v_genres:
                if isinstance(self._genres, str) or not isinstance(self._genres, Iterable):
                    raise Validation_Error("Genres must be a non-string iterable")
                if any(not isinstance(genre, str) or not genre.strip() for genre in self._genres):
                    raise Validation_Error("Empty value in genres")
                
            return result
        return wrapper
    return outer

# ------------------------------------------------------------------------------------------------------------------------------------------------

def validating_user(
    v_username: bool = False, 
    v_email: bool = False, 
    v_role: bool = False
):
    """
    Создаёт декоратор для пост-валидации атрибутов объекта пользователя.

    В зависимости от переданных флагов выполняет проверки атрибутов экземпляра:
    - v_username=True: проверяет, что self._username — непустая строка длиной не менее 3 символов;
    - v_email=True: проверяет, что self._email соответствует формату e‑mail;
    - v_role=True: проверяет, что self._role входит в допустимый набор ролей
      {"user", "admin", "moderator"}.

    Если какая-либо проверка не проходит, возбуждается Validation_Error с
    соответствующим сообщением. Если все активированные проверки проходят,
    метод возвращает свой исходный результат без изменений.
    """
    def outer(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            
            if v_username:
                if not isinstance(self._username, str) or not self._username.strip():
                    raise Validation_Error("Username is empty")
                if len(self._username) < 3:
                     raise Validation_Error("Username must be at least 3 characters long")

            if v_email:
                regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
                if not re.fullmatch(regex, self._email):
                    raise Validation_Error("Invalid email format")

            if v_role and not isinstance(self._role, UserRole):
                raise Validation_Error("Invalid role")
                
            return result
        return wrapper
    return outer

# ------------------------------------------------------------------------------------------------------------------------------------------------

def validating_review(
    v_links: bool = False, 
    v_rating: bool = False, 
    v_status: bool = False
):
    """
    Создаёт декоратор для пост-валидации атрибутов объекта отзыва.

    В зависимости от переданных флагов выполняет следующие проверки полей
    экземпляра:
    - v_links=True:
        проверяет, что self._movie_id > 0 и self._user_id > 0; при нарушении
        выбрасывает Validation_Error;
    - v_rating=True:
        проверяет, что self._rating находится в диапазоне от self.MIN_RATING
        до self.MAX_RATING включительно; при нарушении выбрасывает
        Validation_Error;
    - v_status=True:
        проверяет, что self._status входит в допустимый набор статусов
        {"published", "hidden", "deleted"}; при нарушении выбрасывает
        Validation_Error.

    Если хотя бы одна активированная проверка не проходит, выполнение
    декорируемого метода считается неуспешным, и соответствующее исключение
    пробрасывается наружу. Если все активированные проверки проходят, метод
    возвращает свой исходный результат без изменений.
    """
    def outer(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            
            if v_links :
                if self._movie_id <= 0:
                    raise Validation_Error("movie_id must be a positive integer")
                if self._user_id <= 0:
                    raise Validation_Error("user_id must be a positive integer") 

            if v_rating and not (self.MIN_RATING <= self._rating <= self.MAX_RATING):
                raise Validation_Error(f"Rating must be between {self.MIN_RATING} and {self.MAX_RATING}")

            if v_status and not isinstance(self._status, ReviewStatus):
                raise Validation_Error("Status must be an instance of ReviewStatus")
                
            return result
        return wrapper
    return outer

# ------------------------------------------------------------------------------------------------------------------------------------------------

def sync_by_review_id(func):
    @wraps(func)
    def wrapper(self, review_id: int, *args, **kwargs):
        review = self.get_review(review_id)
        movie_id = review.movie_id
        user_id = review.user_id

        result = func(self, review_id, *args, **kwargs)

        self._recalculate_movie_rating(movie_id)
        self._recalculate_user_review_count(user_id)

        return result
    return wrapper
