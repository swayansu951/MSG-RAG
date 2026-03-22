class TableType:
    NOT_TABLE = 0
    GRID_TABLE = 1
    TEXT_ALIGNED_TABLE = 2
    IMAGE_TABLE = 3
    HYBRID_TABLE = 4

class TableDetector:
    def __init__(self):
        pass

    def detect(self, image, ocr_data):
        signals = self.extract_signals(image, ocr_data)
        table_type = self.classify(signals)
        
        return table_type, signals
    
    def extract_signals(self, image, ocr_data):
        return {
            "grid" : 0.5,
            "alignment" : 0.5,
            "density" : 0.5, 
            "ocr_conf" : 0.5
        }
    
    def classify(self, signals):
        score = (
            0.3 * signals["grid"] + 
            0.3 * signals["alignment"] + 
            0.2 * signals["repetition"] +
            0.1 * signals["density"] + 
            0.1 * signals["ocr_conf"]
        )

        if score < 0.3:
            return TableType.NOT_TABLE
        
        if signals["grid"] > 0.6:
            return TableType.GRID_TABLE
        
        if signals["alignment"] > 0.5:
            # use_table_pipeline()
            return TableType.TEXT_ALIGNED_TABLE
        
        if signals["ocr_conf"] < 0.3:
            return TableType.IMAGE_TABLE
        
        return TableType.HYBRID_TABLE

#  Dummy test
# image = None
# ocr_data = None

# detector = TableDetector()

# table_type, signals = detector.detect(image, ocr_data)

# print("Table Type: " , table_type)
# print("Signals: ", signals)