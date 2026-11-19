"""Place the vector sign (rate-us-on-nfc-sign.pdf) onto the letter cut-guide
pages from print.html (rendered to guides.pdf) at sizes A/B/C."""
import sys
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import NameObject, DictionaryObject

guides = PdfReader(sys.argv[1])
w = PdfWriter()
for i, width in enumerate((7.0, 6.5, 6.0)):
    sign = PdfReader("rate-us-on-nfc-sign.pdf").pages[0]
    s = width / 8.5
    x = (8.5 - width) / 2 * 72
    y = (11 - 2.6 - 5.5 * s) * 72
    page = w.add_page(guides.pages[i])
    page.merge_transformed_page(sign, Transformation().scale(s, s).translate(x, y))
w._root_object[NameObject("/ViewerPreferences")] = DictionaryObject(
    {NameObject("/PrintScaling"): NameObject("/None")})
w.write("PRINT-ME-rate-us-on-sign.pdf")
