from router import DocumentRouter
from table_pipeline import process_table
from text_pipeline import process_text

class DocumentProcessor:
    def __init__(self):
        self.router = DocumentRouter()

    def process(self, image, ocr_data, query):
        router, signals = self.router.router(image, ocr_data)

        if router == "table_pipeline":
            result = process_table(ocr_data, query)

        elif router == "text_pipeline":
            result = process_text(ocr_data, query)

        else:
            result = ("Unknown route", 0.0)
        
        return {
            "route" : router,
            "signals" : signals,
            "result" : result
        }