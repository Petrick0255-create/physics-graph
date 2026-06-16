# app.py

import sys
import matplotlib

matplotlib.use("QtAgg")

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout,
    QFileDialog, QMessageBox, QComboBox, QGroupBox, QTableWidget,
    QTableWidgetItem, QHeaderView
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import matplotlib.pyplot as plt

from peak_graph import draw_peak_graph
from curve_graph import draw_curve_graph


plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


class PhysicsGraphMaker(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("수능 물리 그래프 생성기")
        self.resize(1350, 820)

        self.drag_start = None

        self.graph_type = QComboBox()
        self.graph_type.addItems(["봉우리 곡선 그래프", "구간 그래프"])

        self.x_label_input = QLineEdit("시간")
        self.y_label_input = QTextEdit()
        self.y_label_input.setFixedHeight(75)
        self.y_label_input.setPlainText("힘\n의\n\n크\n기")

        self.x_min_input = QLineEdit("0")
        self.x_max_input = QLineEdit("5")
        self.y_min_input = QLineEdit("0")
        self.y_max_input = QLineEdit("3")
        self.x_ticks_input = QLineEdit("0")
        self.y_ticks_input = QLineEdit("0")

        self.name_input = QLineEdit("A")
        self.peak_height_input = QLineEdit("2.4")

        self.shape_select = QComboBox()
        self.shape_select.addItems(["좁게", "보통", "넓게"])

        self.line_select = QComboBox()
        self.line_select.addItems(["실선", "점선"])

        self.segment_type = QComboBox()
        self.segment_type.addItems(["수평", "완만 변화", "직선", "꺾은선", "감소곡선", "증가곡선"])

        self.seg_start_input = QLineEdit("0")
        self.seg_end_input = QLineEdit("2")
        self.seg_y1_input = QLineEdit("12")
        self.seg_y2_input = QLineEdit("21")
        self.seg_mid_x_input = QLineEdit("")
        self.seg_mid_y_input = QLineEdit("")

        self.add_segment_button = QPushButton("이 구간 그리기")
        self.delete_button = QPushButton("선택 행 삭제")
        self.delete_last_button = QPushButton("마지막 행 삭제")
        self.clear_button = QPushButton("전체 초기화")
        self.preview_button = QPushButton("미리보기")
        self.save_button = QPushButton("PNG 저장")

        self.data_table = QTableWidget(0, 8)
        self.data_table.setHorizontalHeaderLabels([
            "종류/이름", "x1", "x2/y1", "y1/x2", "y2", "그래프", "모양", "선"
        ])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_table.setMinimumHeight(210)

        self.figure = Figure(figsize=(7.5, 4.7))
        self.canvas = FigureCanvas(self.figure)

        self.canvas.mpl_connect("button_press_event", self.on_mouse_press)
        self.canvas.mpl_connect("button_release_event", self.on_mouse_release)

        self.graph_type.currentTextChanged.connect(self.change_graph_type)
        self.segment_type.currentTextChanged.connect(self.change_segment_type)
        self.add_segment_button.clicked.connect(self.add_segment)
        self.delete_button.clicked.connect(self.delete_selected_rows)
        self.delete_last_button.clicked.connect(self.delete_last_row)
        self.clear_button.clicked.connect(self.clear_data)
        self.preview_button.clicked.connect(self.draw_preview)
        self.save_button.clicked.connect(self.save_png)
        self.data_table.itemChanged.connect(self.draw_preview)

        self.build_layout()
        self.change_graph_type()
        self.draw_preview()

    def build_layout(self):
        main = QHBoxLayout()
        left = QVBoxLayout()

        graph_group = QGroupBox("그래프 종류")
        graph_layout = QVBoxLayout()
        graph_layout.addWidget(self.graph_type)
        graph_group.setLayout(graph_layout)

        axis_group = QGroupBox("축 설정")
        axis_layout = QGridLayout()
        axis_layout.addWidget(QLabel("x축 제목"), 0, 0)
        axis_layout.addWidget(self.x_label_input, 0, 1)
        axis_layout.addWidget(QLabel("y축 제목"), 1, 0)
        axis_layout.addWidget(self.y_label_input, 1, 1)
        axis_layout.addWidget(QLabel("x 최솟값"), 2, 0)
        axis_layout.addWidget(self.x_min_input, 2, 1)
        axis_layout.addWidget(QLabel("x 최댓값"), 3, 0)
        axis_layout.addWidget(self.x_max_input, 3, 1)
        axis_layout.addWidget(QLabel("y 최솟값"), 4, 0)
        axis_layout.addWidget(self.y_min_input, 4, 1)
        axis_layout.addWidget(QLabel("y 최댓값"), 5, 0)
        axis_layout.addWidget(self.y_max_input, 5, 1)
        axis_layout.addWidget(QLabel("x축 눈금"), 6, 0)
        axis_layout.addWidget(self.x_ticks_input, 6, 1)
        axis_layout.addWidget(QLabel("y축 눈금"), 7, 0)
        axis_layout.addWidget(self.y_ticks_input, 7, 1)
        axis_group.setLayout(axis_layout)

        self.peak_group = QGroupBox("봉우리 곡선 설정")
        peak_layout = QGridLayout()
        peak_layout.addWidget(QLabel("이름"), 0, 0)
        peak_layout.addWidget(self.name_input, 0, 1)
        peak_layout.addWidget(QLabel("최댓값"), 1, 0)
        peak_layout.addWidget(self.peak_height_input, 1, 1)
        peak_layout.addWidget(QLabel("모양"), 2, 0)
        peak_layout.addWidget(self.shape_select, 2, 1)
        peak_layout.addWidget(QLabel("선"), 3, 0)
        peak_layout.addWidget(self.line_select, 3, 1)
        peak_layout.addWidget(QLabel("그래프 위에서 드래그하면 시작x~끝x가 입력됩니다."), 4, 0, 1, 2)
        self.peak_group.setLayout(peak_layout)

        self.segment_group = QGroupBox("구간 그래프 설정")
        segment_layout = QGridLayout()
        segment_layout.addWidget(QLabel("구간 종류"), 0, 0)
        segment_layout.addWidget(self.segment_type, 0, 1)
        segment_layout.addWidget(QLabel("구간 시작 x"), 1, 0)
        segment_layout.addWidget(self.seg_start_input, 1, 1)
        segment_layout.addWidget(QLabel("구간 끝 x"), 2, 0)
        segment_layout.addWidget(self.seg_end_input, 2, 1)
        segment_layout.addWidget(QLabel("시작값 / 수평값 y"), 3, 0)
        segment_layout.addWidget(self.seg_y1_input, 3, 1)
        segment_layout.addWidget(QLabel("끝값 y"), 4, 0)
        segment_layout.addWidget(self.seg_y2_input, 4, 1)
        segment_layout.addWidget(QLabel("꺾은선 중간 x"), 5, 0)
        segment_layout.addWidget(self.seg_mid_x_input, 5, 1)
        segment_layout.addWidget(QLabel("꺾은선 중간 y"), 6, 0)
        segment_layout.addWidget(self.seg_mid_y_input, 6, 1)
        segment_layout.addWidget(QLabel("모양"), 7, 0)
        segment_layout.addWidget(self.shape_select, 7, 1)
        segment_layout.addWidget(QLabel("선"), 8, 0)
        segment_layout.addWidget(self.line_select, 8, 1)
        segment_layout.addWidget(self.add_segment_button, 9, 0, 1, 2)
        self.segment_group.setLayout(segment_layout)

        button_row = QHBoxLayout()
        button_row.addWidget(self.delete_button)
        button_row.addWidget(self.delete_last_button)
        button_row.addWidget(self.clear_button)

        bottom_row = QHBoxLayout()
        bottom_row.addWidget(self.preview_button)
        bottom_row.addWidget(self.save_button)

        left.addWidget(graph_group)
        left.addWidget(axis_group)
        left.addWidget(self.peak_group)
        left.addWidget(self.segment_group)
        left.addWidget(QLabel("데이터 목록"))
        left.addWidget(self.data_table)
        left.addLayout(button_row)
        left.addLayout(bottom_row)

        main.addLayout(left, 1)
        main.addWidget(self.canvas, 2)

        self.setLayout(main)

    def change_graph_type(self):
        self.clear_data()

        if self.graph_type.currentText() == "봉우리 곡선 그래프":
            self.peak_group.setEnabled(True)
            self.segment_group.setEnabled(False)

            self.x_label_input.setText("시간")
            self.y_label_input.setPlainText("힘\n의\n\n크\n기")
            self.x_min_input.setText("0")
            self.x_max_input.setText("5")
            self.y_min_input.setText("0")
            self.y_max_input.setText("3")
            self.x_ticks_input.setText("0")
            self.y_ticks_input.setText("0")

        else:
            self.peak_group.setEnabled(False)
            self.segment_group.setEnabled(True)

            self.x_label_input.setText("시간(s)")
            self.y_label_input.setPlainText("B\n의\n\n운\n동\n량\n\n(kg·m/s)")
            self.x_min_input.setText("0")
            self.x_max_input.setText("5")
            self.y_min_input.setText("0")
            self.y_max_input.setText("25")
            self.x_ticks_input.setText("0,2,2.2,3,3.1")
            self.y_ticks_input.setText("0,11,12,21")

            self.change_segment_type()

        self.draw_preview()

    def change_segment_type(self):
        mode = self.segment_type.currentText()

        self.seg_y2_input.setEnabled(mode != "수평")
        self.seg_mid_x_input.setEnabled(mode == "꺾은선")
        self.seg_mid_y_input.setEnabled(mode == "꺾은선")
        self.shape_select.setEnabled(mode in ["완만 변화", "감소곡선", "증가곡선"])

    def add_table_row(self, values):
        self.data_table.blockSignals(True)

        row = self.data_table.rowCount()
        self.data_table.insertRow(row)

        for col in range(8):
            text = values[col] if col < len(values) else ""
            self.data_table.setItem(row, col, QTableWidgetItem(str(text)))

        self.data_table.blockSignals(False)

    def add_segment(self):
        try:
            mode = self.segment_type.currentText()
            x1 = float(self.seg_start_input.text())
            x2 = float(self.seg_end_input.text())
            y1 = float(self.seg_y1_input.text())
            line = self.line_select.currentText()
            shape = self.shape_select.currentText()

            if x2 <= x1:
                QMessageBox.warning(self, "확인", "구간 끝 x는 시작 x보다 커야 합니다.")
                return

            if mode == "수평":
                self.add_table_row(["수평", x1, x2, y1, "", "", "", line])

            elif mode == "완만 변화":
                y2 = float(self.seg_y2_input.text())
                self.add_table_row(["변화", x1, x2, y1, y2, "", shape, line])

            elif mode == "직선":
                y2 = float(self.seg_y2_input.text())
                self.add_table_row(["직선", x1, y1, x2, y2, "", "", line])

            elif mode == "꺾은선":
                y2 = float(self.seg_y2_input.text())
                mx = float(self.seg_mid_x_input.text()) if self.seg_mid_x_input.text().strip() else (x1 + x2) / 2
                my = float(self.seg_mid_y_input.text()) if self.seg_mid_y_input.text().strip() else y2
                self.add_table_row(["꺾은선", x1, y1, mx, my, x2, y2, line])

            elif mode in ["감소곡선", "증가곡선"]:
                y2 = float(self.seg_y2_input.text())
                self.add_table_row(["A", x1, x2, y1, y2, mode, shape, line])

            self.draw_preview()

        except ValueError:
            QMessageBox.warning(self, "확인", "숫자 입력칸에 잘못된 값이 있습니다.")

    def table_rows(self):
        rows = []

        for r in range(self.data_table.rowCount()):
            row = []
            for c in range(self.data_table.columnCount()):
                item = self.data_table.item(r, c)
                row.append(item.text().strip() if item else "")
            rows.append(row)

        return rows

    def on_mouse_press(self, event):
        if self.graph_type.currentText() != "봉우리 곡선 그래프":
            return
        if event.xdata is None:
            return
        self.drag_start = event.xdata

    def on_mouse_release(self, event):
        if self.graph_type.currentText() != "봉우리 곡선 그래프":
            return
        if self.drag_start is None or event.xdata is None:
            self.drag_start = None
            return

        start = min(self.drag_start, event.xdata)
        end = max(self.drag_start, event.xdata)
        self.drag_start = None

        if end <= start:
            return

        try:
            height = float(self.peak_height_input.text())
        except ValueError:
            QMessageBox.warning(self, "확인", "봉우리 최댓값을 숫자로 입력하세요.")
            return

        name = self.name_input.text().strip() or "A"
        shape = self.shape_select.currentText()
        line = self.line_select.currentText()

        self.add_table_row([name, f"{start:.2f}", f"{end:.2f}", f"{height:.2f}", shape, line])
        self.draw_preview()

    def parse_numbers(self, text):
        if not text.strip():
            return []
        return [float(x.strip()) for x in text.split(",") if x.strip()]

    def axis_values(self):
        return (
            float(self.x_min_input.text()),
            float(self.x_max_input.text()),
            float(self.y_min_input.text()),
            float(self.y_max_input.text())
        )

    def setup_style(self, ax):
        x_min, x_max, y_min, y_max = self.axis_values()

        x_ticks = self.parse_numbers(self.x_ticks_input.text())
        y_ticks = self.parse_numbers(self.y_ticks_input.text())

        origin_zero_once = x_min == 0 and y_min == 0

        if origin_zero_once:
            x_ticks = [v for v in x_ticks if v != 0]
            y_ticks = [v for v in y_ticks if v != 0]

        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.set_xticks(x_ticks)
        ax.set_yticks(y_ticks)

        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.grid(False)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_linewidth(1.3)
        ax.spines["bottom"].set_linewidth(1.3)

        ax.tick_params(axis="both", labelsize=13, width=1.2, length=5)

        if origin_zero_once:
            ax.text(-0.03, -0.04, "0", transform=ax.transAxes,
                    fontsize=13, ha="right", va="top")

        ax.text(1.03, -0.08, self.x_label_input.text(),
                transform=ax.transAxes, fontsize=15, ha="left", va="top")

        ax.text(-0.12, 1.02, self.y_label_input.toPlainText(),
                transform=ax.transAxes, fontsize=15,
                ha="center", va="bottom", linespacing=0.9)

        ax.annotate("", xy=(1.035, 0), xytext=(0, 0),
                    xycoords="axes fraction",
                    arrowprops=dict(arrowstyle="->", lw=1.3, color="black"))

        ax.annotate("", xy=(0, 1.04), xytext=(0, 0),
                    xycoords="axes fraction",
                    arrowprops=dict(arrowstyle="->", lw=1.3, color="black"))

    def draw_preview(self):
        try:
            self.figure.clear()
            ax = self.figure.add_subplot(111)

            rows = self.table_rows()

            if self.graph_type.currentText() == "봉우리 곡선 그래프":
                draw_peak_graph(ax, rows)
            else:
                draw_curve_graph(ax, rows)

            self.setup_style(ax)

            self.figure.subplots_adjust(left=0.20, right=0.92, bottom=0.18, top=0.88)
            self.canvas.draw()

        except Exception as e:
            QMessageBox.critical(self, "오류", str(e))

    def delete_selected_rows(self):
        selected = sorted(set(i.row() for i in self.data_table.selectedIndexes()), reverse=True)
        for row in selected:
            self.data_table.removeRow(row)
        self.draw_preview()

    def delete_last_row(self):
        row = self.data_table.rowCount()
        if row > 0:
            self.data_table.removeRow(row - 1)
        self.draw_preview()

    def clear_data(self):
        self.data_table.blockSignals(True)
        self.data_table.setRowCount(0)
        self.data_table.blockSignals(False)
        self.draw_preview()

    def save_png(self):
        try:
            self.draw_preview()

            file_path, _ = QFileDialog.getSaveFileName(
                self, "PNG 저장", "graph.png", "PNG Files (*.png)"
            )

            if not file_path:
                return

            if not file_path.lower().endswith(".png"):
                file_path += ".png"

            self.figure.savefig(file_path, dpi=300, transparent=False, bbox_inches="tight")
            QMessageBox.information(self, "완료", "저장 완료")

        except Exception as e:
            QMessageBox.critical(self, "오류", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PhysicsGraphMaker()
    window.show()
    sys.exit(app.exec())