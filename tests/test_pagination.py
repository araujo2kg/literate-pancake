from flaskr.pagination import Pagination


def test_pagination():
    pagination = Pagination(total_items=100)
    assert pagination.page == 1
    assert pagination.per_page == 5
    assert pagination.total_pages == 20
    assert pagination.offset == 0

    pagination2 = Pagination(total_items=100, page=2, per_page=10)
    assert pagination2.page == 2
    assert pagination2.per_page == 10
    assert pagination2.total_pages == 10
    assert pagination2.offset == 10
