from datetime import datetime


def validate_iso_datetime(datetime_str: str) -> datetime:
    """ Валидация и преобразование строки в формат ISO 8601 """
    try:
        dt = datetime.fromisoformat(datetime_str)
        if "T" not in datetime_str:
            raise ValueError("Требуется полный формат с указанием времени")
        return dt
    except ValueError as e:
        raise ValueError(f"Неверный формат даты. Ожидается: ГГГГ-MM-ДДTЧЧ:MM:СС. Ошибка: {str(e)}")


def date_difference_check(dt_from: datetime, dt_upto: datetime) -> bool:
    """ Проверка разницы дат. Если начальная дата больше конечной, возвращает False """
    if dt_upto <= dt_from:
        return False
    return True
