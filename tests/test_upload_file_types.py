import io
import os
import unittest
from pathlib import Path

from src.web_interface.app import create_app


class UploadFileTypesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        # Lower size for testing edge cases
        self.app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
        self.client = self.app.test_client()

    def test_upload_txt(self):
        data = {
            'file': (io.BytesIO(b'hello world'), 'sample.txt')
        }
        resp = self.client.post('/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(resp.status_code, 200)
        j = resp.get_json()
        self.assertEqual(j['file_type'], 'txt')
        self.assertTrue(j['stored_path'].endswith('.txt'))

    def test_upload_pdf(self):
        # create minimal PDF using reportlab
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        c.drawString(100, 750, "Test PDF")
        c.showPage()
        c.save()
        pdf_bytes = buf.getvalue()
        data = {
            'file': (io.BytesIO(pdf_bytes), 'sample.pdf')
        }
        resp = self.client.post('/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(resp.status_code, 200)
        j = resp.get_json()
        self.assertEqual(j['file_type'], 'pdf')
        self.assertTrue(j['stored_path'].endswith('.pdf'))

    def test_upload_docx(self):
        import docx
        buf = io.BytesIO()
        d = docx.Document()
        d.add_paragraph('Hello DOCX')
        d.save(buf)
        docx_bytes = buf.getvalue()
        data = {
            'file': (io.BytesIO(docx_bytes), 'sample.docx')
        }
        resp = self.client.post('/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(resp.status_code, 200)
        j = resp.get_json()
        self.assertEqual(j['file_type'], 'docx')
        self.assertTrue(j['stored_path'].endswith('.docx'))

    def test_upload_unsupported(self):
        data = {
            'file': (io.BytesIO(b'not an image'), 'bad.png')
        }
        resp = self.client.post('/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('仅支持TXT、PDF和DOCX格式', resp.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()