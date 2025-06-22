import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import uuid

def generate_qr_code(lesson, student):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    code = str(uuid.uuid4())
    qr.add_data(f"attendance:{lesson.id}:{student.id}:{code}")
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    file_name = f"qr_{lesson.id}_{student.id}.png"
    content_file = ContentFile(buffer.getvalue(), name=file_name)
    
    return code, content_file