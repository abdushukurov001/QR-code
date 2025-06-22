from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
from .models import User, Class, Subject, Lesson, QRCode, Attendance

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'phone_number', 'role', 'password']
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, data):
      username = data.get('username')
      password = data.get('password')

      if username and password:
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                data['user'] = user
                return data
            else:
                raise serializers.ValidationError("User is disabled.")
        else:
            from rest_framework.exceptions import NotFound
            raise NotFound("User not found.")
      else:
        raise serializers.ValidationError("Username and password are required.")


class ClassSerializer(serializers.ModelSerializer):
    students = UserSerializer(many=True, read_only=True)
    student_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    
    class Meta:
        model = Class
        fields = ['id', 'name', 'students', 'student_ids', 'created_at']
    
    def create(self, validated_data):
        student_ids = validated_data.pop('student_ids', [])
        class_obj = Class.objects.create(**validated_data)
        if student_ids:
            students = User.objects.filter(id__in=student_ids, role='student')
            class_obj.students.set(students)
        return class_obj

class SubjectSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)
    classes = ClassSerializer(many=True, read_only=True)
    class_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'teacher', 'teacher_name', 'classes', 'class_ids']
    
    def create(self, validated_data):
        class_ids = validated_data.pop('class_ids', [])
        subject = Subject.objects.create(**validated_data)
        if class_ids:
            classes = Class.objects.filter(id__in=class_ids)
            subject.classes.set(classes)
        return subject

class LessonSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    class_name = serializers.CharField(source='class_room.name', read_only=True)
    teacher_name = serializers.CharField(source='subject.teacher.full_name', read_only=True)
    
    class Meta:
        model = Lesson
        fields = ['id', 'subject', 'subject_name', 'class_room', 'class_name', 
                 'teacher_name', 'start_time', 'end_time', 'created_at']

class QRCodeSerializer(serializers.ModelSerializer):
    qr_image = serializers.SerializerMethodField()
    lesson_info = serializers.SerializerMethodField()
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    
    class Meta:
        model = QRCode
        fields = ['id', 'code', 'qr_image', 'lesson_info', 'student_name', 'created_at']
    
    def get_qr_image(self, obj):
        return obj.generate_qr_image()
    
    def get_lesson_info(self, obj):
        return {
            'subject': obj.lesson.subject.name,
            'class': obj.lesson.class_room.name,
            'start_time': obj.lesson.start_time,
            'end_time': obj.lesson.end_time
        }

class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    lesson_info = serializers.SerializerMethodField()
    is_present = serializers.SerializerMethodField()
    
    class Meta:
        model = Attendance
        fields = ['id', 'lesson', 'student', 'student_name', 'status', 
                 'marked_at', 'lesson_info', 'is_present', 'created_at']
    
    def get_lesson_info(self, obj):
        return {
            'subject': obj.lesson.subject.name,
            'class': obj.lesson.class_room.name,
            'start_time': obj.lesson.start_time,
            'teacher': obj.lesson.subject.teacher.full_name
        }
    
    def get_is_present(self, obj):
        return obj.status in ['present', 'late']

class MarkAttendanceSerializer(serializers.Serializer):
    qr_code = serializers.CharField()
    
    def validate_qr_code(self, value):
        try:
            qr_obj = QRCode.objects.get(code=value)
            return qr_obj
        except QRCode.DoesNotExist:
            raise serializers.ValidationError('Invalid QR code.')
    
    def mark_attendance(self, qr_obj):
        lesson = qr_obj.lesson
        student = qr_obj.student
        current_time = timezone.now()
        
        time_diff = current_time - lesson.start_time
        
        if time_diff <= timedelta(minutes=15):
            status = 'present'
        elif time_diff <= timedelta(minutes=30):
            status = 'late'
        else:
            status = 'absent'
        
        attendance, created = Attendance.objects.get_or_create(
            lesson=lesson,
            student=student,
            defaults={
                'status': status,
                'marked_at': current_time
            }
        )
        
        if not created:
            attendance.status = status
            attendance.marked_at = current_time
            attendance.save()
        
        return attendance
