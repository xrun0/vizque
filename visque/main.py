import sys
from PySide6.QtWidgets import QApplication
from question.ui.question_window import QuestionWindow
from projection.ui.projection_view import ProjectionView

def main():
    app = QApplication(sys.argv)

    qwin = QuestionWindow()
    pview = ProjectionView()

    # soru penceresinden gelen sonucu projeksiyona ulaştır
    qwin.effectRequested.connect(lambda cell_id, is_correct: pview.show_effect(cell_id, is_correct))

    qwin.show()   # öğretmen/soru penceresi
    # pview zaten full screen açılıyor

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
