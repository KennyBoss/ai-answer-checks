"""Три арифметические проверки ответа ИИ. Python 3.9+, без зависимостей."""

import argparse
from decimal import Decimal, DecimalException, InvalidOperation, localcontext


def number(text):
    try:
        value = Decimal(text)
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError("Нужно число, например 2.5") from exc
    if not value.is_finite():
        raise argparse.ArgumentTypeError("Нужно конечное число")
    if value.is_zero():
        return Decimal(0)
    if not -12 <= value.adjusted() < 13:
        raise argparse.ArgumentTypeError(
            "Слишком большое или маленькое число. Используйте 0 или модуль "
            "от 1e-12 до 1e13, не включая 1e13")
    if len(value.as_tuple().digits) > 50:
        raise argparse.ArgumentTypeError("Допустимо не более 50 значащих цифр")
    return value


def display(value):
    text = format(value, "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def check_total(items, claimed):
    actual = sum(items, Decimal(0))
    return actual, claimed - actual


def percent_change(before, after):
    if not (0 <= before <= 100 and 0 <= after <= 100):
        raise ValueError("Доли должны быть от 0 до 100 процентов")
    points = after - before
    relative = None if before == 0 else points / before * 100
    return points, relative


def speed_change(generation, other, factor):
    if generation < 0 or other < 0 or factor <= 0:
        raise ValueError("Время должно быть неотрицательным, множитель — больше нуля")
    before = generation + other
    if before == 0:
        raise ValueError("Общее исходное время должно быть больше нуля")
    after = generation / factor + other
    return before, after, (before - after) / before * 100, before / after


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    total = sub.add_parser("total", help="Сравнить сумму строк с объявленным итогом")
    total.add_argument("items", type=number, nargs="+")
    total.add_argument("--claimed", type=number, required=True)
    percent = sub.add_parser("percent", help="Сравнить две доли, заданные в процентах")
    percent.add_argument("before", type=number)
    percent.add_argument("after", type=number)
    speed = sub.add_parser("speed", help="Ускорить один этап и пересчитать всё время")
    speed.add_argument("--generation", type=number, required=True, help="Время изменяемого этапа")
    speed.add_argument("--other", type=number, required=True, help="Сумма остальных этапов")
    speed.add_argument("--factor", type=number, required=True, help="Множитель скорости изменяемого этапа")
    args = parser.parse_args()
    try:
        with localcontext() as context:
            context.prec = 50
            if args.command == "total":
                actual, difference = check_total(args.items, args.claimed)
                print(f"Сумма строк: {display(actual)}")
                print(f"Объявленный итог: {display(args.claimed)}")
                print(f"Итог минус сумма: {display(difference)}")
            elif args.command == "percent":
                points, relative = percent_change(args.before, args.after)
                print(f"Изменение в процентных пунктах: {display(points)}")
                print("Относительное изменение: не определено при исходной доле 0%"
                      if relative is None else f"Относительное изменение: {relative:.2f}%")
            else:
                before, after, reduction, multiplier = speed_change(
                    args.generation, args.other, args.factor)
                print(f"Общее время до: {display(before)}")
                print(f"Общее время после: {after:.2f}")
                print(f"Сокращение общего времени: {reduction:.2f}%")
                print(f"Ускорение всей задачи: {multiplier:.4f} раза")
    except (ValueError, DecimalException, OverflowError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
