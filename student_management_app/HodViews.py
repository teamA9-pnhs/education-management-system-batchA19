from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage #To upload Profile Picture
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json

from student_management_app.models import CustomUser, Staffs, Courses, Semester,Semester_OE,Subjects,Subjects_OE,Students, SessionYearModel, FeedBackStudent, FeedBackStaffs, LeaveReportStudent, LeaveReportStaff, Attendance, AttendanceReport, Subjects_OE
from .forms import AddStudentForm, EditStudentForm

#---------------DASHBOARD-----------------------------------#

def admin_home(request):
    all_student_count = Students.objects.all().count()
    subject_count = Subjects.objects.all().count()
    course_count = Courses.objects.all().count()
    staff_count = Staffs.objects.all().count()

    # Total Subjects and students in Each Course
    course_all = Courses.objects.all()
    course_name_list = []
    subject_count_list = []
    student_count_list_in_course = []

    for course in course_all:
        subjects = Subjects.objects.filter(course_id=course.id).count()
        students = Students.objects.filter(course_id=course.id).count()
        course_name_list.append(course.course_name)
        subject_count_list.append(subjects)
        student_count_list_in_course.append(students)
    
    subject_all = Subjects.objects.all()
    subject_list = []
    student_count_list_in_subject = []
    for subject in subject_all:
        course = Courses.objects.get(id=subject.course_id.id)
        student_count = Students.objects.filter(course_id=course.id).count()
        subject_list.append(subject.subject_name)
        student_count_list_in_subject.append(student_count)
    
    # For Saffs
    staff_attendance_present_list=[]
    staff_attendance_leave_list=[]
    staff_name_list=[]

    staffs = Staffs.objects.all()
    for staff in staffs:
        subject_ids = Subjects.objects.filter(staff_id=staff.admin.id)
        attendance = Attendance.objects.filter(subject_id__in=subject_ids).count()
        leaves = LeaveReportStaff.objects.filter(staff_id=staff.id, leave_status=1).count()
        staff_attendance_present_list.append(attendance)
        staff_attendance_leave_list.append(leaves)
        staff_name_list.append(staff.admin.first_name)

    # For Students
    student_attendance_present_list=[]
    student_attendance_leave_list=[]
    student_name_list=[]

    students = Students.objects.all()
    for student in students:
        attendance = AttendanceReport.objects.filter(student_id=student.id, status=True).count()
        absent = AttendanceReport.objects.filter(student_id=student.id, status=False).count()
        leaves = LeaveReportStudent.objects.filter(student_id=student.id, leave_status=1).count()
        student_attendance_present_list.append(attendance)
        student_attendance_leave_list.append(leaves+absent)
        student_name_list.append(student.admin.first_name)


    context={
        "all_student_count": all_student_count,
        "subject_count": subject_count,
        "course_count": course_count,
        "staff_count": staff_count,
        "course_name_list": course_name_list,
        "subject_count_list": subject_count_list,
        "student_count_list_in_course": student_count_list_in_course,
        "subject_list": subject_list,
        "student_count_list_in_subject": student_count_list_in_subject,
        "staff_attendance_present_list": staff_attendance_present_list,
        "staff_attendance_leave_list": staff_attendance_leave_list,
        "staff_name_list": staff_name_list,
        "student_attendance_present_list": student_attendance_present_list,
        "student_attendance_leave_list": student_attendance_leave_list,
        "student_name_list": student_name_list,
    }
    return render(request, "hod_template/home_content.html", context)



#---------------STAFF------------------------------------------------------------------------------------#


def add_staff(request):
    return render(request, "hod_template/add_staff_template.html")


def add_staff_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method ")
        return redirect('add_staff')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')

        try:
            user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=2)
            user.staffs.address = address
            user.save()
            messages.success(request, "Staff Added Successfully!")
            return redirect('add_staff')
        except:
            messages.error(request, "Failed to Add Staff!")
            return redirect('add_staff')



def manage_staff(request):
    staffs = Staffs.objects.all()
    context = {
        "staffs": staffs
    }
    return render(request, "hod_template/manage_staff_template.html", context)


def edit_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)

    context = {
        "staff": staff,
        "id": staff_id
    }
    return render(request, "hod_template/edit_staff_template.html", context)


def edit_staff_save(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        staff_id = request.POST.get('staff_id')
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')

        try:
            # INSERTING into Customuser Model
            user = CustomUser.objects.get(id=staff_id)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.username = username
            user.save()
            
            # INSERTING into Staff Model
            staff_model = Staffs.objects.get(admin=staff_id)
            staff_model.address = address
            staff_model.save()

            messages.success(request, "Staff Updated Successfully.")
            return redirect('/edit_staff/'+staff_id)

        except:
            messages.error(request, "Failed to Update Staff.")
            return redirect('/edit_staff/'+staff_id)



def delete_staff(request, staff_id):
    staff = Staffs.objects.get(admin=staff_id)
    try:
        staff.delete()
        messages.success(request, "Staff Deleted Successfully.")
        return redirect('manage_staff')
    except:
        messages.error(request, "Failed to Delete Staff.")
        return redirect('manage_staff')








#---------------SEMESTER---------------------------------------------------------------------------#




def add_semester(request):
    return render(request, "hod_template/add_semester.html")


def add_semester_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('add_semester')
    else:
        semester = request.POST.get('semester')
        try:
            semester_model = Semester(semester_name=semester)
            semester_model.save()
            messages.success(request, "Semester Added Successfully!")
            return redirect('add_semester')
        except:
            messages.error(request, "Failed to Add Semester!")
            return redirect('add_semester')

def manage_semester(request):
    semesters = Semester.objects.all()
    context = {
        "semesters": semesters
    }
    return render(request, 'hod_template/manage_semester.html', context)


def edit_semester(request, semester_id):
    semester = Semester.objects.get(id=semester_id)
    context = {
        "semester": semester,
        "id": semester_id
    }
    return render(request, 'hod_template/edit_semester.html', context)


def edit_semester_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method")
    else:
        semester_id = request.POST.get('semester_id')
        semester_name = request.POST.get('semester')

        try:
            semester = Semester.objects.get(id=semester_id)
            semester.semester_name = semester_name
            semester.save()

            messages.success(request, "semester Updated Successfully.")
            return redirect('/edit_semester/'+semester_id)

        except:
            messages.error(request, "Failed to Update semester.")
            return redirect('/edit_semester/'+semester_id)


def delete_semester(request, semester_id):
    semester = Semester.objects.get(id=semester_id)
    try:
        semester.delete()
        messages.success(request, "semester Deleted Successfully.")
        return redirect('manage_semester')
    except:
        messages.error(request, "Failed to Delete semester.")
        return redirect('manage_semester')












#---------------OPEN ELECTIVE--------------------------------------------------------------------------#






def open_electives(request):
    elective_semesters = Semester_OE.objects.all()
    context = {
        "electives_semesters": elective_semesters
    }
    return render(request, 'hod_template/open_electives.html', context)
   
def open_electives_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('open_electives')
    else:
        semester = request.POST.get('semester')
        try:
            semester_model = Semester_OE(semester_name=semester)
            semester_model.save()
            messages.success(request, "Semester Added Successfully!")
            return redirect('open_electives')
        except:
            messages.error(request, "Failed to Add Semester!")
            return redirect('open_electives')



def add_sem_open_electives(request):
    return render(request, "hod_template/add_sem_open_electives.html")

def add_sem_open_electives_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('add_sem_open_electives')
    else:
        semester = request.POST.get('semester')
        try:
            semester_model = Semester_OE(semester_name=semester)
            semester_model.save()
            messages.success(request, "Semester Added Successfully!")
            return redirect('add_sem_open_electives')
        except:
            messages.error(request, "Failed to Add Semester!")
            return redirect('add_sem_open_electives')












def add_subj_open_electives(request):
    courses = Courses.objects.all()
    semester = Semester.objects.all()
    staffs = CustomUser.objects.filter(user_type='2')
    context = {
        "courses": courses,
        "staffs": staffs,
        "semesters": semester
    }
    return render(request, 'hod_template/add_subj_open_electives.html', context)




def add_subj_open_electives_save(request):
    if request.method != "POST":
        messages.error(request, "Method Not Allowed!")
        return redirect('add_subj_open_electives')
    else:
        subject_name = request.POST.get('subject')

        course_id = request.POST.get('course')
        course = Courses.objects.get(id=course_id)

        # electives_semesters = request.POST.get('semester_id')
        # semester = Semester_OE.objects.get(id=electives_semesters)
        
        staff_id = request.POST.get('staff')
        staff = CustomUser.objects.get(id=staff_id)

        try:
            subject = Subjects_OE(subject_name=subject_name,course_id=course, staff_id=staff)
            subject.save()
            messages.success(request, "Subject Added Successfully!")
            return redirect('add_subj_open_electives')
        except:
            messages.error(request, "Failed to Add Subject!")
            return redirect('add_subj_open_electives')

    #    subject = Subjects_OE(subject_name=subject_name, course_id=course, semester_id = semester, staff_id=staff)
def manage_subj_open_electives(request):
    elective_subjects = Subjects_OE.objects.all()
    context = {
        "electives_subjects": elective_subjects
    }
    return render(request, 'hod_template/open_electives_subject.html', context)




# def manage_semesterId(request):
#     subjects = Subjects.objects.all()
#     context = {
#         "subjects": subjects
#     }
#     return render(request, 'hod_template/manage_semesterId.html', context)

def edit_subj_open_electives(request, subject_id):
    subject = Subjects_OE.objects.get(id=subject_id)
    courses = Courses.objects.all()
    semester = Semester.objects.all()
    staffs = CustomUser.objects.filter(user_type='2')
    context = {
        "subject": subject,
        "courses": courses,
        "semesters" : semester,
        "staffs": staffs,
        "id": subject_id
    }
    return render(request, 'hod_template/edit_subject_open_electives.html', context)


def edit_subj_open_electives_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method.")
    else:
        subject_id = request.POST.get('subject_id')
        subject_name = request.POST.get('subject')
        semester_id = request.POST.get('semester_id')
        course_id = request.POST.get('course')
        staff_id = request.POST.get('staff')

        try:
            subject = Subjects_OE.objects.get(id=subject_id)
            subject.subject_name = subject_name

            course = Courses.objects.get(id=course_id)
            subject.course_id = course

            semester = Semester.objects.get(id=semester_id)
            subject.semester_id = semester

            staff = CustomUser.objects.get(id=staff_id)
            subject.staff_id = staff
            
            subject.save()

            messages.success(request, "Subject Updated Successfully.")
            # return redirect('/edit_subject/'+subject_id)
            return HttpResponseRedirect(reverse("edit_subject_open_electives", kwargs={"subject_id":subject_id}))

        except:
            messages.error(request, "Failed to Update Subject.")
            return HttpResponseRedirect(reverse("edit_subject_open_electives", kwargs={"subject_id":subject_id}))
            # return redirect('/edit_subject/'+subject_id)



def delete_subj_open_electives(request, subject_id):
    subject = Subjects_OE.objects.get(id=subject_id)
    try:
        subject.delete()
        messages.success(request, "Subject Deleted Successfully.")
        return redirect('manage_subj_open_electives')
    except:
        messages.error(request, "Failed to Delete Subject.")
        return redirect('manage_subj_open_electives')




#---------------COURSE---------------------------------------------------------------------------#





def add_course(request):
    return render(request, "hod_template/add_course_template.html")


def add_course_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('add_course')
    else:
        course = request.POST.get('course')
        try:
            course_model = Courses(course_name=course)
            course_model.save()
            messages.success(request, "Course Added Successfully!")
            return redirect('add_course')
        except:
            messages.error(request, "Failed to Add Course!")
            return redirect('add_course')




def manage_course(request):
    courses = Courses.objects.all()
    context = {
        "courses": courses
    }
    return render(request, 'hod_template/manage_course_template.html', context)


def edit_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    context = {
        "course": course,
        "id": course_id
    }
    return render(request, 'hod_template/edit_course_template.html', context)


def edit_course_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method")
    else:
        course_id = request.POST.get('course_id')
        course_name = request.POST.get('course')

        try:
            course = Courses.objects.get(id=course_id)
            course.course_name = course_name
            course.save()

            messages.success(request, "Course Updated Successfully.")
            return redirect('/edit_course/'+course_id)

        except:
            messages.error(request, "Failed to Update Course.")
            return redirect('/edit_course/'+course_id)


def delete_course(request, course_id):
    course = Courses.objects.get(id=course_id)
    try:
        course.delete()
        messages.success(request, "Course Deleted Successfully.")
        return redirect('manage_course')
    except:
        messages.error(request, "Failed to Delete Course.")
        return redirect('manage_course')




#---------------SESSION---------------------------------------------------------------------------#


def manage_session(request):
    session_years = SessionYearModel.objects.all()
    context = {
        "session_years": session_years
    }
    return render(request, "hod_template/manage_session_template.html", context)


def add_session(request):
    return render(request, "hod_template/add_session_template.html")


def add_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('add_course')
    else:
        session_start_year = request.POST.get('session_start_year')
        session_end_year = request.POST.get('session_end_year')

        try:
            sessionyear = SessionYearModel(session_start_year=session_start_year, session_end_year=session_end_year)
            sessionyear.save()
            messages.success(request, "Session Year added Successfully!")
            return redirect("add_session")
        except:
            messages.error(request, "Failed to Add Session Year")
            return redirect("add_session")


def edit_session(request, session_id):
    session_year = SessionYearModel.objects.get(id=session_id)
    context = {
        "session_year": session_year
    }
    return render(request, "hod_template/edit_session_template.html", context)


def edit_session_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('manage_session')
    else:
        session_id = request.POST.get('session_id')
        session_start_year = request.POST.get('session_start_year')
        session_end_year = request.POST.get('session_end_year')

        try:
            session_year = SessionYearModel.objects.get(id=session_id)
            session_year.session_start_year = session_start_year
            session_year.session_end_year = session_end_year
            session_year.save()

            messages.success(request, "Session Year Updated Successfully.")
            return redirect('/edit_session/'+session_id)
        except:
            messages.error(request, "Failed to Update Session Year.")
            return redirect('/edit_session/'+session_id)


def delete_session(request, session_id):
    session = SessionYearModel.objects.get(id=session_id)
    try:
        session.delete()
        messages.success(request, "Session Deleted Successfully.")
        return redirect('manage_session')
    except:
        messages.error(request, "Failed to Delete Session.")
        return redirect('manage_session')





#---------------STUDENT---------------------------------------------------------------------------#

def add_student(request):
    # form = AddStudentForm()
    subjects = Subjects.objects.all()
    session_years = SessionYearModel.objects.all()
    semester = Semester.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years,
        "semesters": semester,
        # "form": form
    }
    return render(request, "hod_template/add_student_template.html", context)  



import re
def add_student_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method ")
        return redirect('add_student')
    
    elif request.FILES.get('student_file'):
        studentFile = request.FILES['student_file']
        fileText = studentFile.read().decode('utf-8')
        print(fileText,  " thiS IS THE FILE TEXT")
        regex = "2SD%"
        line = re.split('\n',fileText)
        print(line ," thIS IS THE SEPARATED LINE");
    #    print(Sess_start +" And " + Sess_end)
        for x in line[:-1]:
            # m = re.match('(\d)? (.*)\S',x)
            m = re.split('\t',x)
            print(m , "THIS IS MMMMMMMMMMM")
            print(m[1])
        #    if(m[0] != "Session Start:"):
            print(m)
            raw_name = m[1]
            name= re.split('\s',raw_name)
            first_name = name[0]
            last_name =name[1]
            print(first_name + " " + last_name + " THIs is the first name and the last name")
            for l in m:
                if(l.isnumeric()):
                    print(l + " This is a number ")
                elif re.match(r'^2SD',l) :
                    print("Username: " +l)
                    username= l;
                elif re.match(r'\S+@\S+',l):
                    print("email" +l)
                    email = l
                elif re.match('Male',l) or re.match('Female',l):
                    sex = l.replace('\r','')

            password="student"
            address= "Goa"
            session_year_id = request.POST.get('session_year_id')
            try:
                print("Creating")
                print( username + " | " + password + " | " + email + " | " + first_name+ " | " + last_name + " | " + sex)
                user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=3)
                # Students.objects.create(admin=user, course_id=Courses.objects.get(id=1), session_year_id=SessionYearModel.objects.get(id=1), address="", profile_pic="", gender="")
                print(user , "Created")
                user.students.address = address
                print("Address")
                session_year_obj = SessionYearModel.objects.get(id=session_year_id)
                semester_name = request.POST.get('semester_id')
                # semister_obj=Semisters.objects.get(id=semister_id)
                user.students.semester_id=semester_name
                # user.students.session_start_year=session_start
                # user.students.session_end_year=session_end
                user.students.session_year_id = session_year_obj
                user.students.gender=sex
                user.students.profile_pics=""
                print("Just saving the student")
                user.save()
                print("Saved, He's all our")
                messages.success(request, "Student Added Successfully!")
                return redirect('add_student')
            except BaseException as err:
                print(f"Unexpected {err=}, {type(err)=}")
                messages.error(request, "Failed to Add Student!")
                return redirect('add_student')
                print( " Not able to add any students now")
                
        return redirect('add_student')

    else:

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')
        semester_id =request.POST.get('semester_id')
        session_year_id = request.POST.get('session_year_id')
        course_id = request.POST.get('course_id')
        gender = request.POST.get('sex')


        # form = AddStudentForm(request.POST, request.FILES)

        # if form.is_valid():
        #     first_name = form.cleaned_data['first_name']
        #     last_name = form.cleaned_data['last_name']
        #     username = form.cleaned_data['username']
        #     email = form.cleaned_data['email']
        #     password = form.cleaned_data['password']
        #     address = form.cleaned_data['address']
        #     semester_id = form.cleaned_data['semester_id']
        #     session_year_id = form.cleaned_data['session_year_id']
        #     course_id = form.cleaned_data['course_id']
        #     gender = form.cleaned_data['sex']

        try:
                user = CustomUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name, user_type=3)
                user.students.address = address
                user.students.semester = semester_id

                course_obj = Courses.objects.get(id=course_id)
                user.students.course_id = course_obj

                semester_obj = Semester.objects.get(id=semester_id)
                user.students.semester_id = semester_obj

                session_year_obj = SessionYearModel.objects.get(id=session_year_id)
                user.students.session_year_id = session_year_obj

                user.students.gender = gender
                user.students.profile_pics=""
                # user.students.profile_pic = profile_pic_url
                user.save()
                messages.success(request, "Student Added Successfully!")
                return redirect('add_student')
        except:
            messages.error(request, "Failed to Add Student!")
            return redirect('add_student')






def manage_student(request):
    students = Students.objects.all()
    context = {
        "students": students
    }
    return render(request, 'hod_template/manage_student_template.html', context)


def edit_student(request, student_id):
    # Adding Student ID into Session Variable
    request.session['student_id'] = student_id

    student = Students.objects.get(admin=student_id)
    form = EditStudentForm()
    # Filling the form with Data from Database
    form.fields['email'].initial = student.admin.email
    form.fields['username'].initial = student.admin.username
    form.fields['first_name'].initial = student.admin.first_name
    form.fields['last_name'].initial = student.admin.last_name
    form.fields['address'].initial = student.address
    form.fields['semester_id'].initial = student.semester_id.id
    form.fields['course_id'].initial = student.course_id.id
    form.fields['gender'].initial = student.gender
    form.fields['session_year_id'].initial = student.session_year_id.id

    context = {
        "id": student_id,
        "username": student.admin.username,
        "form": form
    }
    return render(request, "hod_template/edit_student_template.html", context)


def edit_student_save(request):
    if request.method != "POST":
        return HttpResponse("Invalid Method!")
    else:
        student_id = request.session.get('student_id')
        if student_id == None:
            return redirect('/manage_student')

        form = EditStudentForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            address = form.cleaned_data['address']
            semester_id = form.cleaned_data['semester_id']
            course_id = form.cleaned_data['course_id']
            gender = form.cleaned_data['gender']
            session_year_id = form.cleaned_data['session_year_id']

            # Getting Profile Pic first
            # First Check whether the file is selected or not
            # Upload only if file is selected
            if len(request.FILES) != 0:
                profile_pic = request.FILES['profile_pic']
                fs = FileSystemStorage()
                filename = fs.save(profile_pic.name, profile_pic)
                profile_pic_url = fs.url(filename)
            else:
                profile_pic_url = None

            try:
                # First Update into Custom User Model
                user = CustomUser.objects.get(id=student_id)
                user.first_name = first_name
                user.last_name = last_name
                user.email = email
                user.username = username
                user.save()

                # Then Update Students Table
                student_model = Students.objects.get(admin=student_id)
                student_model.address = address

                course = Courses.objects.get(id=course_id)
                student_model.course_id = course

                semester = Semester.objects.get(id=semester_id)
                student_model.semester_id = semester

                session_year_obj = SessionYearModel.objects.get(id=session_year_id)
                student_model.session_year_id = session_year_obj

                student_model.gender = gender
                if profile_pic_url != None:
                    student_model.profile_pic = profile_pic_url
                student_model.save()
                # Delete student_id SESSION after the data is updated
                del request.session['student_id']

                messages.success(request, "Student Updated Successfully!")
                return redirect('/edit_student/'+student_id)
            except:
                messages.success(request, "Failed to Uupdate Student.")
                return redirect('/edit_student/'+student_id)
        else:
            return redirect('/edit_student/'+student_id)


def delete_student(request, student_id):
    student = Students.objects.get(admin=student_id)
    try:
        student.delete()
        messages.success(request, "Student Deleted Successfully.")
        return redirect('manage_student')
    except:
        messages.error(request, "Failed to Delete Student.")
        return redirect('manage_student')





#---------------SUBJECT---------------------------------------------------------------------------#



def add_subject(request):
    courses = Courses.objects.all()
    semester = Semester.objects.all()
    staffs = CustomUser.objects.filter(user_type='2')
    context = {
        "courses": courses,
        "staffs": staffs,
        "semesters": semester
    }
    return render(request, 'hod_template/add_subject_template.html', context)



def add_subject_save(request):
    if request.method != "POST":
        messages.error(request, "Method Not Allowed!")
        return redirect('add_subject')
    else:
        subject_name = request.POST.get('subject')

        course_id = request.POST.get('course')
        course = Courses.objects.get(id=course_id)

        semesters = request.POST.get('semester_id')
        semester = Semester.objects.get(id=semesters)
        
        staff_id = request.POST.get('staff')
        staff = CustomUser.objects.get(id=staff_id)

        try:
            subject = Subjects(subject_name=subject_name, course_id=course, semester_id = semester, staff_id=staff)
            subject.save()
            messages.success(request, "Subject Added Successfully!")
            return redirect('add_subject')
        except:
            messages.error(request, "Failed to Add Subject!")
            return redirect('add_subject')


def manage_subject(request):
    subjects = Subjects.objects.all()
    context = {
        "subjects": subjects
    }
    return render(request, 'hod_template/manage_subject_template.html', context)

def manage_semesterId(request):
    subjects = Subjects.objects.all()
    context = {
        "subjects": subjects
    }
    return render(request, 'hod_template/manage_semesterId.html', context)

def edit_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    courses = Courses.objects.all()
    semester = Semester.objects.all()
    staffs = CustomUser.objects.filter(user_type='2')
    context = {
        "subject": subject,
        "courses": courses,
        "semesters" : semester,
        "staffs": staffs,
        "id": subject_id
    }
    return render(request, 'hod_template/edit_subject_template.html', context)


def edit_subject_save(request):
    if request.method != "POST":
        HttpResponse("Invalid Method.")
    else:
        subject_id = request.POST.get('subject_id')
        subject_name = request.POST.get('subject')
        semester_id = request.POST.get('semester_id')
        course_id = request.POST.get('course')
        staff_id = request.POST.get('staff')

        try:
            subject = Subjects.objects.get(id=subject_id)
            subject.subject_name = subject_name

            course = Courses.objects.get(id=course_id)
            subject.course_id = course

            semester = Semester.objects.get(id=semester_id)
            subject.semester_id = semester

            staff = CustomUser.objects.get(id=staff_id)
            subject.staff_id = staff
            
            subject.save()

            messages.success(request, "Subject Updated Successfully.")
            # return redirect('/edit_subject/'+subject_id)
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id":subject_id}))

        except:
            messages.error(request, "Failed to Update Subject.")
            return HttpResponseRedirect(reverse("edit_subject", kwargs={"subject_id":subject_id}))
            # return redirect('/edit_subject/'+subject_id)



def delete_subject(request, subject_id):
    subject = Subjects.objects.get(id=subject_id)
    try:
        subject.delete()
        messages.success(request, "Subject Deleted Successfully.")
        return redirect('manage_subject')
    except:
        messages.error(request, "Failed to Delete Subject.")
        return redirect('manage_subject')



#---------------CSRF TOKENS---------------------------------------------------------------------------#



@csrf_exempt
def check_email_exist(request):
    email = request.POST.get("email")
    user_obj = CustomUser.objects.filter(email=email).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)

@csrf_exempt
def check_course_exist(request):
    course= request.POST.get("course")
    course_obj = Courses.objects.filter(course_name=course).exists()
    if course_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_subject_exist(request):
    subject= request.POST.get("subject")
    subject_obj = Subjects.objects.filter(subject_name=subject).exists()
    if subject_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)


@csrf_exempt
def check_username_exist(request):
    username = request.POST.get("username")
    user_obj = CustomUser.objects.filter(username=username).exists()
    if user_obj:
        return HttpResponse(True)
    else:
        return HttpResponse(False)



def student_feedback_message(request):
    feedbacks = FeedBackStudent.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'hod_template/student_feedback_template.html', context)


@csrf_exempt
def student_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedBackStudent.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")


def staff_feedback_message(request):
    feedbacks = FeedBackStaffs.objects.all()
    context = {
        "feedbacks": feedbacks
    }
    return render(request, 'hod_template/staff_feedback_template.html', context)


@csrf_exempt
def staff_feedback_message_reply(request):
    feedback_id = request.POST.get('id')
    feedback_reply = request.POST.get('reply')

    try:
        feedback = FeedBackStaffs.objects.get(id=feedback_id)
        feedback.feedback_reply = feedback_reply
        feedback.save()
        return HttpResponse("True")

    except:
        return HttpResponse("False")


def student_leave_view(request):
    leaves = LeaveReportStudent.objects.all()
    context = {
        "leaves": leaves
    }
    return render(request, 'hod_template/student_leave_view.html', context)

def student_leave_approve(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return redirect('student_leave_view')


def student_leave_reject(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return redirect('student_leave_view')


def staff_leave_view(request):
    leaves = LeaveReportStaff.objects.all()
    context = {
        "leaves": leaves
    }
    return render(request, 'hod_template/staff_leave_view.html', context)


def staff_leave_approve(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 1
    leave.save()
    return redirect('staff_leave_view')


def staff_leave_reject(request, leave_id):
    leave = LeaveReportStaff.objects.get(id=leave_id)
    leave.leave_status = 2
    leave.save()
    return redirect('staff_leave_view')


def admin_view_attendance(request):
    subjects = Subjects.objects.all()
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request, "hod_template/admin_view_attendance.html", context)


@csrf_exempt
def admin_get_attendance_dates(request):
    # Getting Values from Ajax POST 'Fetch Student'
    subject_id = request.POST.get("subject")
    session_year = request.POST.get("session_year_id")

    # Students enroll to Course, Course has Subjects
    # Getting all data from subject model based on subject_id
    subject_model = Subjects.objects.get(id=subject_id)

    session_model = SessionYearModel.objects.get(id=session_year)

    # students = Students.objects.filter(course_id=subject_model.course_id, session_year_id=session_model)
    attendance = Attendance.objects.filter(subject_id=subject_model, session_year_id=session_model)

    # Only Passing Student Id and Student Name Only
    list_data = []

    for attendance_single in attendance:
        data_small={"id":attendance_single.id, "attendance_date":str(attendance_single.attendance_date), "session_year_id":attendance_single.session_year_id.id}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@csrf_exempt
def admin_get_attendance_student(request):
    # Getting Values from Ajax POST 'Fetch Student'
    attendance_date = request.POST.get('attendance_date')
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    # Only Passing Student Id and Student Name Only
    list_data = []

    for student in attendance_data:
        data_small={"id":student.student_id.admin.id, "name":student.student_id.admin.first_name+" "+student.student_id.admin.last_name, "status":student.status}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


def admin_profile(request):
    user = CustomUser.objects.get(id=request.user.id)

    context={
        "user": user
    }
    return render(request, 'hod_template/admin_profile.html', context)


def admin_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('admin_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()
            messages.success(request, "Profile Updated Successfully")
            return redirect('admin_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('admin_profile')
    


def staff_profile(request):
    pass


def student_profile(request):
    pass




def search_student(request):
     return render(request, 'hod_template/search_student.html')



def search_student(request):
	if request.method == "POST":
		searched = request.POST['searched']
		search_results = CustomUser.objects.filter(username__contains=searched)
	
		return render(request,'hod_template/search_student.html',{'searched':searched,'search_results':search_results})
	else:
		return render(request,'hod_template/search_student.html',{})
    
def search_staff(request):
	if request.method == "POST":
		searched = request.POST['searched']
		search_results = CustomUser.objects.filter(username__contains=searched)
	
		return render(request,'hod_template/search_staff.html',{'searched':searched,'search_results':search_results})
	else:
		return render(request,'hod_template/search_staff.html',{})


# def search_student(request):
# 	if request.method == "POST":
# 		searched = request.POST['searched']
# 		search_results = Students.objects.filter(admin_id__contains=searched)
	
# 		return render(request,'hod_template/search_student.html',{'searched':searched,'search_results':search_results})
# 	else:
# 		return render(request,'hod_template/search_student.html',{})
