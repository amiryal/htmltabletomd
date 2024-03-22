import html2markdown

from bs4 import BeautifulSoup


def _transform_cell_content(value: str, conversion_ind: bool = False) -> str:
    if value and conversion_ind is True:
        value = html2markdown.convert(value)
    chars = {"|": "&#124;", "\n": "<br>"}
    for char, replacement in chars.items():
        value = value.replace(char, replacement)
    return value


ALIGNMENT_OPTIONS = {"left": " :--- ", "center": " :---: ", "right": " ---: "}


def convert_table(
    html: str, content_conversion_ind: bool = False, all_cols_alignment: str = "left"
) -> str:
    if all_cols_alignment not in ALIGNMENT_OPTIONS.keys():
        raise ValueError(
            "Invalid alignment option for {!r} arg. "
            "Expected one of: {}".format(
                "all_cols_alignment", list(ALIGNMENT_OPTIONS.keys())
            )
        )

    soup = BeautifulSoup(html, "html.parser")

    if not soup.find():
        return html

    table = []
    table_headings = []
    table_body = []
    table_tr = soup.find_all("tr")

    try:
        table_headings = [
            " "
            + _transform_cell_content(
                th.renderContents().decode("utf-8"),
                conversion_ind=content_conversion_ind,
            )
            + " "
            for th in soup.find("tr").find_all("th")
        ]
    except AttributeError:
        raise ValueError("No {!r} tag found".format("tr"))

    if table_headings:
        table.append(table_headings)
        table_tr = table_tr[1:]

    for tr in table_tr:
        td_list = []
        for td in tr.find_all("td"):
            td_list.append(
                " "
                + _transform_cell_content(
                    td.renderContents().decode("utf-8"),
                    conversion_ind=content_conversion_ind,
                )
                + " "
            )
        table_body.append(td_list)

    table += table_body
    md_table_header = "|".join(
        [""]
        + ([" "] * len(table[0]) if not table_headings else table_headings)
        + ["\n"]
        + [ALIGNMENT_OPTIONS[all_cols_alignment]] * len(table[0])
        + ["\n"]
    )

    md_table = md_table_header + "".join(
        "|".join([""] + row + ["\n"]) for row in table_body
    )
    return md_table


def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        prog="HTML Table to GF-Markdown converter",
        description="Convert an HTML table Markdown syntax",
        epilog="Reads one HTML table from standard input and writes Markdown to standard output.",
    )
    alignment_choices = list(ALIGNMENT_OPTIONS.keys())
    parser.add_argument(
        "--align", choices=alignment_choices, default=alignment_choices[0]
    )
    parser.add_argument(
        "--convert-cells",
        action="store_true",
        help="convert contents inside table cells",
    )
    args = parser.parse_args()
    input = sys.stdin.read()
    output = convert_table(
        input, all_cols_alignment=args.align, content_conversion_ind=args.convert_cells
    )
    sys.stdout.write(output)


if __name__ == "__main__":
    main()
