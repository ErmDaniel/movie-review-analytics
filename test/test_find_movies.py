import pytest
from movie.models import Movie
from movie.service import MovieReviewService

@pytest.fixture
def service_with_movies():
    svc = MovieReviewService()
    svc.add_movie(Movie(_id=1, _title="Inception", _release_year=2010,
                        _genres=["Sci-Fi", "Thriller"]))
    svc.add_movie(Movie(_id=2, _title="The Dark Knight", _release_year=2008,
                        _genres=["Action", "Crime"]))
    svc.add_movie(Movie(_id=3, _title="Interstellar", _release_year=2014,
                        _genres=["Sci-Fi", "Drama"]))
    
    svc._movies[1].set_rating([8, 9, 7])   # avg = 8.0
    svc._movies[2].set_rating([9, 10, 9])  # avg = 9.33
    svc._movies[3].set_rating([8, 8])      # avg = 8.0
    return svc

def test_find_by_genre(service_with_movies):
    result = service_with_movies.find_movies(genre="Sci-Fi")
    assert len(result) == 2
    assert all("Sci-Fi" in m._genres for m in result)

def test_find_by_year_range(service_with_movies):
    result = service_with_movies.find_movies(year_from=2009, year_to=2013)
    assert len(result) == 1
    assert result[0]._title == "Inception"

def test_find_by_min_rating(service_with_movies):
    result = service_with_movies.find_movies(min_avg_rating=9.0)
    assert len(result) == 1
    assert result[0]._title == "The Dark Knight"

def test_find_combined(service_with_movies):
    result = service_with_movies.find_movies(genre="Sci-Fi", min_avg_rating=8.0)
    assert len(result) == 2  # Inception и Interstellar

def test_find_no_results(service_with_movies):
    result = service_with_movies.find_movies(genre="Horror")
    assert result == []

def test_find_title_contains(service_with_movies):
    result = service_with_movies.find_movies(title_contains="dark")
    assert result[0]._title == "The Dark Knight"