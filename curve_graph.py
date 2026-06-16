# curve_graph.py

import numpy as np


def get_linestyle(line_style):
    return "--" if line_style == "점선" else "-"


def smoothstep(t):
    """
    t=0, t=1에서 기울기가 0인 부드러운 연결 함수
    """
    return 3 * t**2 - 2 * t**3


def smooth_value(t, shape):
    if shape == "좁게":
        s = smoothstep(t)
        return smoothstep(s)

    if shape == "넓게":
        return 0.5 - 0.5 * np.cos(np.pi * t)

    return smoothstep(t)


def draw_curve_graph(ax, rows):
    """
    표 데이터 기준

    수평:
    종류 | x1 | x2 | y1 | 빈칸 | 빈칸 | 빈칸 | 선

    변화:
    종류 | x1 | x2 | y1 | y2 | 빈칸 | 모양 | 선

    직선:
    종류 | x1 | y1 | x2 | y2 | 빈칸 | 빈칸 | 선

    꺾은선:
    종류 | x1 | y1 | 중간x | 중간y | x2 | y2 | 선

    감소곡선/증가곡선:
    이름 | x1 | x2 | y1 | y2 | 그래프 | 모양 | 선
    """

    guide_points = set()

    for row in rows:
        if len(row) < 8:
            continue

        kind = row[0]

        if kind == "수평":
            result = draw_horizontal(ax, row)

        elif kind == "변화":
            result = draw_smooth_change(ax, row)

        elif kind == "직선":
            result = draw_line(ax, row)

        elif kind == "꺾은선":
            result = draw_polyline(ax, row)

        else:
            result = draw_named_curve(ax, row)

        if result:
            for point in result:
                guide_points.add(point)

    draw_guides(ax, guide_points)


def draw_horizontal(ax, row):
    try:
        start = float(row[1])
        end = float(row[2])
        y = float(row[3])
    except ValueError:
        return None

    line_style = row[7]
    linestyle = get_linestyle(line_style)

    if end <= start:
        return None

    ax.hlines(
        y,
        start,
        end,
        linewidth=2.5,
        color="black",
        linestyle=linestyle,
        zorder=3
    )

    return [
        (start, y),
        (end, y)
    ]


def draw_smooth_change(ax, row):
    try:
        start = float(row[1])
        end = float(row[2])
        y1 = float(row[3])
        y2 = float(row[4])
    except ValueError:
        return None

    shape = row[6] or "보통"
    line_style = row[7]
    linestyle = get_linestyle(line_style)

    if end <= start:
        return None

    x = np.linspace(start, end, 600)
    t = (x - start) / (end - start)

    s = smooth_value(t, shape)
    y = y1 + (y2 - y1) * s

    ax.plot(
        x,
        y,
        linewidth=2.5,
        color="black",
        linestyle=linestyle,
        zorder=3
    )

    return [
        (start, y1),
        (end, y2)
    ]


def draw_line(ax, row):
    try:
        x1 = float(row[1])
        y1 = float(row[2])
        x2 = float(row[3])
        y2 = float(row[4])
    except ValueError:
        return None

    line_style = row[7]
    linestyle = get_linestyle(line_style)

    ax.plot(
        [x1, x2],
        [y1, y2],
        linewidth=2.5,
        color="black",
        linestyle=linestyle,
        zorder=3
    )

    return [
        (x1, y1),
        (x2, y2)
    ]


def draw_polyline(ax, row):
    try:
        x1 = float(row[1])
        y1 = float(row[2])
        mx = float(row[3])
        my = float(row[4])
        x2 = float(row[5])
        y2 = float(row[6])
    except ValueError:
        return None

    line_style = row[7]
    linestyle = get_linestyle(line_style)

    ax.plot(
        [x1, mx, x2],
        [y1, my, y2],
        linewidth=2.5,
        color="black",
        linestyle=linestyle,
        zorder=3
    )

    return [
        (x1, y1),
        (mx, my),
        (x2, y2)
    ]


def draw_named_curve(ax, row):
    try:
        name = row[0]
        start = float(row[1])
        end = float(row[2])
        y1 = float(row[3])
        y2 = float(row[4])
    except ValueError:
        return None

    curve_type = row[5]
    shape = row[6] or "보통"
    line_style = row[7]
    linestyle = get_linestyle(line_style)

    if curve_type not in ["감소곡선", "증가곡선"]:
        return None

    if end <= start:
        return None

    x = np.linspace(start, end, 600)
    t = (x - start) / (end - start)

    s = smooth_value(t, shape)
    y = y1 + (y2 - y1) * s

    ax.plot(
        x,
        y,
        linewidth=2.4,
        color="black",
        linestyle=linestyle,
        zorder=3
    )

    if name:
        ax.text(
            (start + end) / 2,
            (y1 + y2) / 2,
            name,
            fontsize=14,
            ha="left",
            va="center"
        )

    return [
        (start, y1),
        (end, y2)
    ]


def draw_guides(ax, guide_points):
    """
    보조 점선은 그래프를 뚫고 지나가지 않고,
    축과 그래프 점 사이에만 존재함.

    각 점 (x, y)에 대해:
    - 세로 점선: (x, 0) → (x, y)
    - 가로 점선: (0, y) → (x, y)
    """

    for x, y in sorted(guide_points):
        if abs(x) < 1e-9 and abs(y) < 1e-9:
            continue

        if abs(x) > 1e-9:
            ax.plot(
                [x, x],
                [0, y],
                color="black",
                linewidth=0.9,
                linestyle="dotted",
                alpha=0.55,
                zorder=1
            )

        if abs(y) > 1e-9:
            ax.plot(
                [0, x],
                [y, y],
                color="black",
                linewidth=0.9,
                linestyle="dotted",
                alpha=0.55,
                zorder=1
            )