import argparse
from collections import defaultdict


class RuHelpFormatter(argparse.HelpFormatter):
    def __init__(self, prog):
        super().__init__(prog)

    def _format_usage(
        self, usage, actions, groups, prefix
    ):
        prefix = "\n[+] Использование: "

        return super()._format_usage(usage, actions, groups, prefix)


class RuErrorFormatter(argparse.ArgumentParser):
    def error(self, message):
        if "invalid choice" in message and "--report" in message:
            choices = self._option_string_actions['--report'].choices
            message = f"----------\n  ОШИБКА: Недопустимый вариант отчета (выберите из доступных: {', '.join(choices)})\n----------"
        elif "the following arguments are required" in message:
            message = " [+] ОШИБКА: Требуются следующие аргументы: " + message.split(":")[-1].strip()

        self.print_help()
        self.exit(2, f"\n{message}\n")


def auto_choices_in_parse_report(parser_arg, choices: dict) -> None:

    if not choices:
        raise ValueError("[+] ERROR: Список choices (варианты формирования отчетов) не может быть пустым")

    parser_arg.add_argument(
        '--report',
        choices=choices,
        required=True,
        help="Формирование отчёта ( доступные варианты: " + ", ".join([el_comd for el_comd in choices]) + " )"
    )

    print("\n[+] Описание:\n\t" + "\n\t".join(f"{cmd} — {desc}" for cmd, desc in choices.items()) + "\n")


def create_handlers_report(data: dict) -> str:
    """
        :parameter data:
            Словарь с данными логов

        :return:
            Возврат отчета
    """

    sorted_data = sorted(
        data.keys(),
        # key=lambda element: -len(element) # Для красивого вывода с большого на меньший
    )

    report_handlers_skeleton = [
        "\t\t  +_______________________________________+\n"
        "\t\t  |\t  ТАБЛИЦА ПО ОТЧЕТУ HANDLERS\t  |"
        "\n+--------------------------+-----------+----------+-----------+----------+----------+",
        "|        HANDLER           |   DEBUG   |   INFO   |  WARNING  |   ERROR  | CRITICAL |",
        "|--------------------------|-----------|----------|-----------|----------|----------|"
    ]

    total = 0

    for handler in sorted_data:
        counts = data[handler]
        row = (
            f"| {handler.ljust(24)} | "
            f"{str(counts.get('DEBUG', 0)).center(9)} | "
            f"{str(counts.get('INFO', 0)).center(8)} | "
            f"{str(counts.get('WARNING', 0)).center(9)} | "
            f"{str(counts.get('ERROR', 0)).center(8)} | "
            f"{str(counts.get('CRITICAL', 0)).center(8)} |"
        )
        report_handlers_skeleton.append(row)

        total += sum(counts.values())

    report_handlers_skeleton.append("+" + "-" * 83 + "+")

    report_handlers_skeleton.append(f"\n\t\t\tВсего логов [ django.request ]: {total}\n")

    return "\n".join(report_handlers_skeleton)


def _parse_line(file_line: str, data: dict) -> None:
    if "django.request" in file_line:
        file_line_split = file_line.split()

        log_level = file_line_split[2] if len(file_line_split) > 2 else None
        log_url = next((url for url in file_line_split if str(url).startswith("/")), None)

        if log_level and log_url:
            data[log_url][log_level] += 1


def _parse_file(file_path, data) -> None:
    try:
        with open(file_path, "r", encoding="UTF-8") as file:
            for line in file:
                _parse_line(line, data)
    except FileNotFoundError:
        print(f"\n[+] Файл: {file_path} не найден! Проверьте коректность ссылки на файл!\n")


def parse_log(file_links: list[str]) -> dict[str, dict[str, int]]:
    data = defaultdict(lambda: defaultdict(int))

    for file_path in file_links:
        _parse_file(file_path, data)

    return data


def main(choices_dict):
    parser = RuErrorFormatter(
        formatter_class=RuHelpFormatter,
        add_help=False
    )

    parser._optionals.title = "[+] Опциональные команды"
    parser.add_argument(
        '-h', '--help',
        action='help',
        default=argparse.SUPPRESS,
        help='Помощь по программе'
    )

    parser._positionals.title = "[+] Позиционные аргументы"
    parser.add_argument(
        "file",
        nargs="+",
        help="Путь до [ *.log | *.txt ] файлов"
    )

    auto_choices_in_parse_report(parser_arg=parser, choices=choices_dict)
    args = parser.parse_args()

    return args


def beautiful_print(color1, color2, color3):
    print(
        f"\n{color1}-----------------------------------------{color3}"
        f"\n{color1}|{color3}\t{color2}АНАЛИЗ ЖУРНАЛОВ ЛОГИРОВАНИЯ{color3}\t{color1}|{color3}\n"
        f"{color1}-----------------------------------------{color3}"
    )


def usual_print():
    print(
        f"\n-----------------------------------------"
        f"\n|\tАНАЛИЗ ЖУРНАЛОВ ЛОГИРОВАНИЯ\t|\n"
        f"-----------------------------------------"
    )


class AnalyzerLogReport:
    def __init__(self):
        self.reports = {
            "handlers": create_handlers_report,
            # Название Отчета и функция отчета
        }


if __name__ == '__main__':

    # Цвета для ВЫВОД
    GREEN = "\033[1;32m"
    ELL_BOLD = "\033[1;36m"
    RESET = "\033[0m"
    # beautiful_print(GREEN, ELL_BOLD, RESET) # Красивый ВЫВОД

    # Обычный ВЫВОД
    usual_print()

    choices_dict = {
        'handlers': "Отчет по ручкам [ django.request ]",
        # ... Варианты Новых Отчётов прописать тут [ "название": "описание" ]
    }

    args = main(choices_dict)
    analiz_file = AnalyzerLogReport()
    data = parse_log(args.file)
    create_print_report = analiz_file.reports[args.report](data)

    print(create_print_report)