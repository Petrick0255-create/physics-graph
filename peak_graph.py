# peak_graph.py

import numpy as np


def draw_peak_graph(ax, rows):
    """
    표 데이터 기준

    봉우리 행 구조:
    종류/이름 | x1 | x2 | 최댓값 | 모양 | 선

    예:
    A | 0.50 | 2.80 | 2.40 | 보통 | 실선
    """

    for row in rows:
        if len(row) < 6:
            continue

        name = row[0]

        try:
            start = float(row[1])
            end = float(row[2])
            max_value = float(row[3])
        except ValueError:
            continue

        shape = row[4]
        line_style = row[5]

        if end <= start:
            continue

        center = (start + end) / 2
        half_width = (end - start) / 2

        if half_width <= 0:
            continue

        x = np.linspace(start, end, 600)

        if shape == "좁게":
            sigma = half_width / 3.2
        elif shape == "넓게":
            sigma = half_width / 1.8
        else:
            sigma = half_width / 2.5

        raw = np.exp(-((x - center) ** 2) / (2 * sigma ** 2))
        edge_raw = np.exp(-((start - center) ** 2) / (2 * sigma ** 2))

        y = max_value * (raw - edge_raw) / (1 - edge_raw)
        y = np.maximum(y, 0)

        linestyle = "--" if line_style == "점선" else "-"

        ax.plot(
            x,
            y,
            linewidth=2.4,
            color="black",
            linestyle=linestyle
        )

        ax.text(
            center,
            max_value * 1.04,
            name,
            fontsize=15,
            ha="center",
            va="bottom"
        )