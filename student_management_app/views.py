# from channels.auth import login, logout
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from random import randint
from django.core.mail import send_mail
from student_management_app.EmailBackEnd import EmailBackEnd


def home(request):
    return render(request, 'index.html')


def loginPage(request):
    return render(request, 'login.html')

def go_here(request):
    if request.method == 'GET':
       return render(request , 'index.html')

def reset_password(request):
    if not 'email' in request.POST is None:
        email = request.POST.get('email')
        print(email)
    else:
        return redirect('index.html')
    if not get_user_model().objects.filter(email= email):
        return render(request, 'otp_not_exist.html' )
    return render(request, 'index2.html',{'otp1_email': email })
  

def verify_otp(request):
    if 'otp_email' in request.POST:
        print(f"Process of checking the otp {request.POST.get('otp_email')} HANG ON!")
        user = get_user_model().objects.get(email=request.POST.get('otp_email'))
        key = user.random_key
        print(key)
        if key == request.POST.get('OTP'):
            return render(request, 'index3.html',{'email':request.POST.get('otp_email')})
        return render(request, 'otpSignIn.html', {'message':"Your OTP is wrong, Enter Again!",'otp1_email':request.POST.get('otp_email')})
    return (request, 'otpSignIn.html',{'message':"Well optemail not found",'otp1_email':request.POST.get('otp_email')})

def sending_email(request):
    if 'otp_email' in request.POST:
        user= get_user_model().objects.get(email=request.POST.get('otp_email'))
        user.random_key = randint(100000, 999999)
        user.save()
        key = user.random_key
        email_mesg ='Well you forgot your email So I\'m here now. Your key for new password is ' + str(key)
        print(email_mesg)
        # send_mail("Reset Password OTP",email_mesg , email ,[request.POST.get('otp_email')], fal_silently=False)
        return render(request, "otpSignIn.html",{"otp1_email": request.POST.get('otp_email')})
    print("not working")
    return render(request, "index.html")

def change_password(request):
    if(request.POST.get('password1')==request.POST.get('password2')):
        User = get_user_model().objects.get(email=request.POST.get('otp_email'))
        User.set_password(request.POST.get('password1'))
        User.save()
        print("well the passwords were same so the password was changed")
        return render(request, 'login.html',{'message':"Your password has been successfully changed!"})
    else:
        print("Things went bad, abort mission!")
        return render(request, 'index3.html', {'message':"Passwords don't match each other",'email':request.POST.get('otp_email')})



def doLogin(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        user = EmailBackEnd.authenticate(request, username=request.POST.get('email'), password=request.POST.get('password'))
        if user != None:
            login(request, user)
            user_type = user.user_type
            #return HttpResponse("Email: "+request.POST.get('email')+ " Password: "+request.POST.get('password'))
            if user_type == '1':
                return redirect('admin_home')
                
            elif user_type == '2':
                # return HttpResponse("Staff Login")
                return redirect('staff_home')
                
            elif user_type == '3':
                # return HttpResponse("Student Login")
                return redirect('student_home')
            else:
                messages.error(request, "Invalid Login!")
                return redirect('login')
        else:
            messages.error(request, "Invalid Login Credentials!")
            #return HttpResponseRedirect("/")
            return redirect('login')



def get_user_details(request):
    if request.user != None:
        return HttpResponse("User: "+request.user.email+" User Type: "+request.user.user_type)
    else:
        return HttpResponse("Please Login First")



def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')


