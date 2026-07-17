def get_color(level):
    if level[-2] == "A":
        return "level-a"
    elif level[-2] == "B":
        return "level-b"
    elif level[-2] == "C":
        return "level-c"
    else:
        return "level-a"


def word_count_label(count):
    if count == 1:
        return "słówko"

    if count % 10 in [2, 3, 4] and count % 100 not in [12, 13, 14]:
        return "słówka"

    return "słówek"


def set_label(count):
    if count == 1:
        return "zestaw"

    if count % 100 in {12, 13, 14}:
        return "zestawów"

    if count % 10 in {2, 3, 4}:
        return "zestawy"

    return "zestawów"


def ready_sets_label(count):
    if count == 1:
        return "gotowy zestaw"

    if count % 100 in {12, 13, 14}:
        return "gotowych zestawów"

    if count % 10 in {2, 3, 4}:
        return "gotowe zestawy"

    return "gotowych zestawów"


def day_label(count):
    return "dzień" if count == 1 else "dni"