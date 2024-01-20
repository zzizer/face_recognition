from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add_student', views.add_student, name='add_student'),
    path('all_students', views.all_students, name='all_students'),
    path('student_details/<str:id>/', views.student_details, name='student_details'),
    path('generate_face_encodings/', views.generate_face_encodings, name='generate_face_encodings'), 
    path('recognize_student/', views.recognize_student, name='recognize_student'),       
]
