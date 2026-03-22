from ingestion.table_detection import TableDetector, TableType

class DocumentRouter:
    def __init__(self):
        self.detector = TableDetector()

    def router(self, image, ocr_data):
        table_type, signals = self.detector.detect(image, ocr_data)

        if table_type != TableType.NOT_TABLE : return "table_pipeline" , signals
        # if diagram : return "diagram_pipeline"
        return "text_pipeline" , signals
    