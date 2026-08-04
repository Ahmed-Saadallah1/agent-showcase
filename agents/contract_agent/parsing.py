import os
os.environ['TORCHDYNAMO_DISABLE'] = '1'

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat

_pipeline_options = PdfPipelineOptions()
_pipeline_options.do_ocr = True
_pipeline_options.do_table_structure = True

_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=_pipeline_options)
    }
)


def parse_contract(file_path: str) -> str:
    '''
    Parse a contract file (PDF or DOCX) into clean, structured markdown.

    OCR is enabled so scanned/image-based contracts (common for older
    business documents) can still be read, not just digitally-generated
    PDFs. torch.compile is disabled globally (see TORCHDYNAMO_DISABLE
    above) since this machine has no C++ compiler for it to use -- this
    lets both layout detection and OCR run reliably in plain mode.
    '''
    result = _converter.convert(file_path)
    return result.document.export_to_markdown()
