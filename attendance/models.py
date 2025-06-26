from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import qrcode
from PIL import Image
import io
import base64
import uuid

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    phone_number = models.CharField(max_length=15, unique=True)
    full_name = models.CharField(max_length=100)
    
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.phone_number
        if not self.password or not self.password.startswith('pbkdf2_'):
            self.set_password(self.full_name.replace(' ', '').lower())
        super().save(*args, **kwargs)

class Class(models.Model):
    name = models.CharField(max_length=50)
    students = models.ManyToManyField(User, related_name='student_classes', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subjects')
    classes = models.ManyToManyField(Class, related_name='subjects')
    
    def __str__(self):
        return f"{self.name} - {self.teacher.full_name}"

class Lesson(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='lessons')
    class_room = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='lessons')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.subject.name} - {self.class_room.name} - {self.start_time}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        for student in self.class_room.students.all():
            QRCode.objects.get_or_create(
                lesson=self,
                student=student,
                defaults={'code': str(uuid.uuid4())}
            )

class QRCode(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='qr_codes')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='qr_codes')
    code = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def generate_qr_image(self):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(self.code)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    def __str__(self):
        return f"QR for {self.student.full_name} - {self.lesson}"

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('late', 'Late'),
        ('absent', 'Absent'),
    ]
    
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='absent')
    marked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['lesson', 'student']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.lesson} - {self.status}"
