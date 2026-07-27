from words.services.labels import (get_color,
                                   word_count_label,
                                   set_label,
                                   ready_sets_label,
                                   day_label,
                                   )


def test_get_color_returns_correct_class_for_level():
    assert get_color("A1") == "level-a"
    assert get_color("B1") == "level-b"
    assert get_color("C1") == "level-c"


def test_word_count_label_returns_correct_form():
    assert word_count_label(1) == "słówko"
    assert word_count_label(4) == "słówka"
    assert word_count_label(12) == "słówek"
    assert word_count_label(21) == "słówek"


def test_set_label_returns_correct_form():
    assert set_label(1) == "zestaw"
    assert set_label(4) == "zestawy"
    assert set_label(12) == "zestawów"
    assert set_label(21) == "zestawów"


def test_ready_sets_label_returns_correct_form():
    assert ready_sets_label(1) == "gotowy zestaw"
    assert ready_sets_label(4) == "gotowe zestawy"
    assert ready_sets_label(12) == "gotowych zestawów"
    assert ready_sets_label(21) == "gotowych zestawów"


def test_day_label_returns_correct_form():
    assert day_label(1) == "dzień"
    assert day_label(2) == "dni"
    assert day_label(12) == "dni"

