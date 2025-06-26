from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from drf_yasg import openapi
from django.core.cache import cache
import random
from django.utils import timezone
from django.db.models import Q
from .models import User, Class, Subject, Lesson, QRCode, Attendance
from .serializers import (
    UserSerializer, LoginSerializer, ClassSerializer, SubjectSerializer,
    LessonSerializer, QRCodeSerializer, AttendanceSerializer, MarkAttendanceSerializer, ForgotPasswordSerializer,ResetPasswordSerializer
)



@swagger_auto_schema(
    method='post',
    request_body=ForgotPasswordSerializer,
    responses={
        200: 'Reset code sent to user',
        400: 'Invalid phone number'
    },
    operation_description="Send reset code to user's phone number"
)
@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_view(request):
    serializer = ForgotPasswordSerializer(data=request.data)
    if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number']

        code = str(random.randint(100000, 999999))

        cache.set(f'reset_code_{phone_number}', code, timeout=300)

        print(f"Reset code for {phone_number}: {code}")

        return Response({'message': 'Reset code sent successfully'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@swagger_auto_schema(
    method='post',
    request_body=ResetPasswordSerializer,
    responses={
        200: 'Password reset successfully',
        400: 'Invalid data or token'
    },
    operation_description="Reset password using token"
)
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_view(request):
    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





@swagger_auto_schema(
    method='post',
    request_body=LoginSerializer,
    responses={
        200: 'Token returned',
        400: 'Invalid credentials'
    },
    operation_description="Authenticate user and get JWT tokens"
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    request_body=UserSerializer,
    responses={
        201: 'User created and token returned',
        400: 'Invalid data'
    },
    operation_description="Register a new user"
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('role', openapi.IN_QUERY, description="Filter by role", type=openapi.TYPE_STRING)
    ],
    responses={200: UserSerializer(many=True)},
    operation_description="List all users (admin only)"
)
@swagger_auto_schema(
    method='post',
    request_body=UserSerializer,
    responses={
        201: 'User created',
        400: 'Invalid data',
        403: 'Permission denied'
    },
    operation_description="Create a new user (admin only)"
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def users_view(request):
    if request.method == 'GET':
        role = request.GET.get('role')
        users = User.objects.all()
        if role:
            users = users.filter(role=role)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if request.user.role != 'admin':
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='get',
    responses={
        200: UserSerializer,
        404: 'User not found'
    },
    operation_description="Get user details"
)
@swagger_auto_schema(
    method='put',
    request_body=UserSerializer,
    responses={
        200: 'User updated',
        400: 'Invalid data',
        403: 'Permission denied',
        404: 'User not found'
    },
    operation_description="Update user details"
)
@swagger_auto_schema(
    method='delete',
    responses={
        204: 'User deleted',
        403: 'Permission denied',
        404: 'User not found'
    },
    operation_description="Delete a user (admin only)"
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def user_detail_view(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        if request.user.role != 'admin' and request.user.id != user.id:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if request.user.role != 'admin':
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        user.delete()
        return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

# Class Management
@swagger_auto_schema(
    method='get',
    responses={200: ClassSerializer(many=True)},
    operation_description="List all classes"
)
@swagger_auto_schema(
    method='post',
    request_body=ClassSerializer,
    responses={
        201: 'Class created',
        400: 'Invalid data',
        403: 'Permission denied'
    },
    operation_description="Create a new class (admin only)"
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def classes_view(request):
    if request.method == 'GET':
        classes = Class.objects.all()
        serializer = ClassSerializer(classes, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if request.user.role != 'admin':
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ClassSerializer(data=request.data)
        if serializer.is_valid():
            class_obj = serializer.save()
            return Response(ClassSerializer(class_obj).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='get',
    responses={
        200: ClassSerializer,
        404: 'Class not found'
    },
    operation_description="Get class details"
)
@swagger_auto_schema(
    method='put',
    request_body=ClassSerializer,
    responses={
        200: 'Class updated',
        400: 'Invalid data',
        403: 'Permission denied',
        404: 'Class not found'
    },
    operation_description="Update class details (admin only)"
)
@swagger_auto_schema(
    method='delete',
    responses={
        204: 'Class deleted',
        403: 'Permission denied',
        404: 'Class not found'
    },
    operation_description="Delete a class (admin only)"
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def class_detail_view(request, class_id):
    try:
        class_obj = Class.objects.get(id=class_id)
    except Class.DoesNotExist:
        return Response({'error': 'Class not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = ClassSerializer(class_obj)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        if request.user.role != 'admin':
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ClassSerializer(class_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        if request.user.role != 'admin':
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        class_obj.delete()
        return Response({'message': 'Class deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

@swagger_auto_schema(
    method='get',
    responses={200: SubjectSerializer(many=True)},
    operation_description="List all subjects"
)
@swagger_auto_schema(
    method='post',
    request_body=SubjectSerializer,
    responses={
        201: 'Subject created',
        400: 'Invalid data',
        403: 'Permission denied'
    },
    operation_description="Create a new subject (admin only)"
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def subjects_view(request):
    if request.method == 'GET':
        subjects = Subject.objects.all()
        if request.user.role == 'admin':
            subjects = subjects.filter(teacher=request.user)
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if request.user.role != 'admin':
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            subject = serializer.save()
            return Response(SubjectSerializer(subject).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('date', openapi.IN_QUERY, description="Filter by date (YYYY-MM-DD)", type=openapi.TYPE_STRING)
    ],
    responses={200: LessonSerializer(many=True)},
    operation_description="List all lessons"
)
@swagger_auto_schema(
    method='post',
    request_body=LessonSerializer,
    responses={
        201: 'Lesson created',
        400: 'Invalid data',
        403: 'Permission denied'
    },
    operation_description="Create a new lesson (admin only)"
)
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def lessons_view(request):
    if request.method == 'GET':
        lessons = Lesson.objects.all()
        
        if request.user.role == 'teacher':
            lessons = lessons.filter(subject__teacher=request.user)
        elif request.user.role == 'student':
            lessons = lessons.filter(class_room__students=request.user)
        
       
        date = request.GET.get('date')
        if date:
            lessons = lessons.filter(start_time__date=date)
        
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if request.user.role != 'admin':
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = LessonSerializer(data=request.data)
        if serializer.is_valid():
            lesson = serializer.save()
            return Response(LessonSerializer(lesson).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('date', openapi.IN_QUERY, description="Filter by date (YYYY-MM-DD)", type=openapi.TYPE_STRING)
    ],
    responses={
        200: QRCodeSerializer(many=True),
        403: 'Permission denied'
    },
    operation_description="Get QR codes for current student"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_qr_codes_view(request):
    if request.user.role != 'student':
        return Response({'error': 'Only students can access QR codes'}, status=status.HTTP_403_FORBIDDEN)
    
    qr_codes = QRCode.objects.filter(student=request.user)
    
   
    date = request.GET.get('date')
    if date:
        qr_codes = qr_codes.filter(lesson__start_time__date=date)
    
    serializer = QRCodeSerializer(qr_codes, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='get',
    responses={
        200: QRCodeSerializer,
        403: 'Permission denied',
        404: 'QR code not found'
    },
    operation_description="Get QR code details"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def qr_code_detail_view(request, qr_id):
    try:
        qr_code = QRCode.objects.get(id=qr_id)
    except QRCode.DoesNotExist:
        return Response({'error': 'QR code not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.user.role == 'student' and qr_code.student != request.user:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = QRCodeSerializer(qr_code)
    return Response(serializer.data)

@swagger_auto_schema(
    method='post',
    request_body=MarkAttendanceSerializer,
    responses={
        201: AttendanceSerializer,
        400: 'Invalid data',
        403: 'Permission denied'
    },
    operation_description="Mark attendance using QR code (teacher only)"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_attendance_view(request):
    if request.user.role != 'teacher':
        return Response({'error': 'Only teachers can mark attendance'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = MarkAttendanceSerializer(data=request.data)
    if serializer.is_valid():
        qr_obj = serializer.validated_data['qr_code']
        
        if qr_obj.lesson.subject.teacher != request.user:
            return Response({'error': 'You are not authorized to mark attendance for this lesson'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        attendance = serializer.mark_attendance(qr_obj)
        return Response(AttendanceSerializer(attendance).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('class_id', openapi.IN_QUERY, description="Filter by class ID", type=openapi.TYPE_INTEGER),
        openapi.Parameter('subject_id', openapi.IN_QUERY, description="Filter by subject ID", type=openapi.TYPE_INTEGER),
        openapi.Parameter('date', openapi.IN_QUERY, description="Filter by date (YYYY-MM-DD)", type=openapi.TYPE_STRING)
    ],
    responses={200: AttendanceSerializer(many=True)},
    operation_description="List attendance records"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attendance_list_view(request):
    attendances = Attendance.objects.all()
    
    if request.user.role == 'teacher':
        attendances = attendances.filter(lesson__subject__teacher=request.user)
    elif request.user.role == 'student':
        attendances = attendances.filter(student=request.user)
    
    class_id = request.GET.get('class_id')
    if class_id:
        attendances = attendances.filter(lesson__class_room_id=class_id)
    
    subject_id = request.GET.get('subject_id')
    if subject_id:
        attendances = attendances.filter(lesson__subject_id=subject_id)
    
    date = request.GET.get('date')
    if date:
        attendances = attendances.filter(lesson__start_time__date=date)
    
    serializer = AttendanceSerializer(attendances, many=True)
    return Response(serializer.data)

@swagger_auto_schema(
    method='get',
    responses={200: 'Dashboard statistics'},
    operation_description="Get dashboard statistics based on user role"
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
    user = request.user
    data = {}
    
    if user.role == 'admin':
        data = {
            'total_students': User.objects.filter(role='student').count(),
            'total_teachers': User.objects.filter(role='teacher').count(),
            'total_classes': Class.objects.count(),
            'total_subjects': Subject.objects.count(),
            'total_lessons': Lesson.objects.count(),
        }
    
    elif user.role == 'teacher':
        today = timezone.now().date()
        data = {
            'my_subjects': Subject.objects.filter(teacher=user).count(),
            'today_lessons': Lesson.objects.filter(
                subject__teacher=user,
                start_time__date=today
            ).count(),
            'total_students': User.objects.filter(
                student_classes__subjects__teacher=user
            ).distinct().count(),
        }
    
    elif user.role == 'student':
        today = timezone.now().date()
        data = {
            'my_classes': user.student_classes.count(),
            'today_lessons': Lesson.objects.filter(
                class_room__students=user,
                start_time__date=today
            ).count(),
            'my_attendance_rate': calculate_attendance_rate(user),
        }
    
    return Response(data)

def calculate_attendance_rate(student):
    total_lessons = Lesson.objects.filter(class_room__students=student).count()
    if total_lessons == 0:
        return 0
    
    present_count = Attendance.objects.filter(
        student=student,
        status__in=['present', 'late']
    ).count()
    
    return round((present_count / total_lessons) * 100, 2)