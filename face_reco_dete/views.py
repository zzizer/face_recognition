from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.core.management import call_command
from .models import Student
from .forms import StudentForm
import cv2
import face_recognition
import numpy as np

def index(request):
    return render(request, 'index.html')
    
def student_details(request, id):
    student = Student.objects.get(id=id)

    content = {
        'student': student,
    }

    return render(request, 'student_details.html', content)


def all_students(request):
    students = Student.objects.all()

    content = {
        'students': students,
    }

    return render(request, 'allstudents.html', content)

def generate_face_encodings(request):
    students = Student.objects.all()

    for student in students:
        # Check if the face encoding already exists for the student
        if student.face_encoding:
            continue

        image_path = student.photo.path

        # Use OpenCV for face detection
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  # Read the image as grayscale
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(image, scaleFactor=1.3, minNeighbors=5)

        if len(faces) == 0:
            # Handle the case where no face is detected
            # You might want to log this or display a message
            continue

        # Extract the face region
        x, y, w, h = faces[0]
        face_region = image[y:y+h, x:x+w]

        # Convert the grayscale image to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

        # Use face_recognition to generate face encoding
        encoding = face_recognition.face_encodings(rgb_image, [(y, x + w, y + h, x)])[0]

        # Store the encoding as bytes in the database
        student.face_encoding = encoding.tobytes()
        student.save()

    messages.success(request, 'Face encodings generated successfully.')

    return redirect('index')


def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            photo = form.cleaned_data['photo']

            # Create a new Student instance without setting face_encoding
            student = Student(name=name, photo=photo)
            student.save()

            messages.success(request, 'Student added successfully.')

            return redirect('all_students')

    else:
        form = StudentForm()

    return render(request, 'add_student.html', {'form': form})


def recognize_student(request):
    # Open the default camera (you may need to change the index if you have multiple cameras)
    cap = cv2.VideoCapture(0)

    while True:
        # Capture a single frame
        ret, frame = cap.read()

        # Display the frame
        cv2.imshow('Video', frame)

        # Break the loop and close the camera when the 'c' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('c'):
            break

    # Release the camera
    cap.release()
    cv2.destroyAllWindows()

    # Detect face locations and encodings in the captured frame
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    if face_encodings:
        # Load known face encodings and names from the database
        students = Student.objects.all()

        # Retrieve stored face encodings from the database
        known_face_encodings = [np.frombuffer(student.face_encoding, dtype=np.float64) for student in students]
        known_face_names = [student.name for student in students]

        # Compare the captured face encoding with known face encodings
        matches = face_recognition.compare_faces(known_face_encodings, face_encodings[0])

        # If a match is found, use the name of the first matching student
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
            return render(request, 'recognize_student.html', {'name': name})
    
    # If no match is found or no face is detected, return 'Unknown'
    return render(request, 'recognize_student.html', {'name': 'Unknown'})