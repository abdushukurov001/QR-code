from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from attendance.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/auth/login/', login_view, name='login'),
    path('api/auth/register/', register_view, name='register'),
    path('api/auth/forgot-password/', forgot_password_view, name='forgot_password'),
    path('api/auth/reset-password/', reset_password_view, name='reset_password'),
    
    path('api/users/', users_view, name='users'),
    path('api/users/<int:user_id>/', user_detail_view, name='user_detail'),
    
    path('api/classes/', classes_view, name='classes'),
    path('api/classes/<int:class_id>/', class_detail_view, name='class_detail'),
    

    path('api/subjects/', subjects_view, name='subjects'),
    
    path('api/lessons/', lessons_view, name='lessons'),
    
    path('api/my-qr-codes/', student_qr_codes_view, name='student_qr_codes'),
    path('api/qr-codes/<int:qr_id>/', qr_code_detail_view, name='qr_code_detail'),
    
    path('api/mark-attendance/', mark_attendance_view, name='mark_attendance'),
    path('api/attendance/', attendance_list_view, name='attendance_list'),
    
    path('api/dashboard/', dashboard_view, name='dashboard'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
