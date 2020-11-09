from django.shortcuts import render
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views import View
import json
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.template.loader import render_to_string
from .utils import account_activation_token
from django.urls import reverse
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import threading




#class to speed up the email sending
class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email =  email
        threading.Thread.__init__(self) 

    def run(self):
        self.email.send(fail_silently=False)




# Create your views here.
class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error': 'username should only contain alphanumeric characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'sorry username in use,choose another one '}, status=409)
        return JsonResponse({'username_valid': True})

class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({'email_error': 'Email is invalid'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'sorry email in use, choose another one '}, status=409)
        return JsonResponse({'email_valid': True})

class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')

    def post(self, request):
        # GET USER DATA
        # VALIDATE
        # create a user account
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        #contains all the value in de post, want to keep values after errors
        context = {
            'fieldValues': request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, 'Mot de passe trop court, 6 caractèress minimum')
                    return render(request, 'authentication/register.html', context)

                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()

                current_site = get_current_site(request)
               
                email_body = {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user),
                }

                link = reverse('activate', kwargs={
                               'uidb64': email_body['uid'], 'token': email_body['token']})

                email_subject = 'Activate your account'

                activate_url = 'http://'+current_site.domain+link

                email = EmailMessage(
                    email_subject,
                    'Hi '+user.username + ', Please follow the link below to activate your account \n'+activate_url,
                    'noreply@badol.com',
                    [email],
                )
                
                EmailThread(email).start()            
                messages.success(request, 'Votre compte Badol a bien été créé, connectez-vous')
                return render(request, 'authentication/login.html', context)
  
        return render(request, 'authentication/register.html')

#account activation view
class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not account_activation_token.check_token(user, token):
                return redirect('login'+'?message='+'User already activated')

            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()

            messages.success(request, 'Account activated successfully')
            return redirect('login')

        except Exception as ex:
            pass

        return redirect('login')

class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, 'Welcome, ' +
                                     user.username+' you are now logged in')
                    return redirect('home')
                messages.error(
                    request, 'Account is not active,please check your email')
                return render(request, 'authentication/login.html')
            messages.error(
                request, 'Invalid credentials,try again')
            return render(request, 'authentication/login.html')

        messages.error(
            request, 'Please fill all fields')
        return render(request, 'authentication/login.html')

class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')

class RequestPasswordResetdEmailView(View):
    def get(self, request):
        return render(request, 'authentication/reset-password.html')

    def post(self, request):

        email =  request.POST['email']

        context = {
            'values': request.POST
        }

        if not validate_email(email):
            messages.error('email invalide')
            return render(request, 'authentication/reset-password.html', context)
            

        user = User.objects.filter(email=email)
        current_site = get_current_site(request)

        if user.exists():
            email_content = {
                        'user': user[0],
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                        'token': PasswordResetTokenGenerator().make_token(user[0]),
                    }
            
            link = reverse('reset-user-password', kwargs={
                                'uidb64': email_content['uid'], 'token': email_content['token']})

            email_subject = 'Mise à jour du mot de pass'

            reset_url = 'http://'+current_site.domain+link

            email = EmailMessage(
                        email_subject,
                        'Salut veuilliez cliquer le lien ci-dessous pour mettre à jour votre mot de passe \n'+reset_url,
                        'noreply@badol.com',
                        [email],
                    )
                    
            EmailThread(email).start()            
            messages.success(request, 'Un email avec un lien vous été envoyé !!')
            return render(request, 'authentication/reset-password.html', context)
        else:
            messages.error(request, 'Aucun utilisateur ne possède cet email')
            return render(request, 'authentication/reset-password.html', context)

class CompletePasswordReset(View):

    def get(self, request, uidb64, token):

        context = {
            'uidb64': uidb64,
            'token': token
        }

        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(request, 'Ce lien est invalide, demandez un nouveau lien')
                return render(request, 'authentication/reset-password.html')

        except Exception as identifier:
            pass

        return render(request, 'authentication/set-new-password.html', context)
        

    
    def post(self, request, uidb64, token):

        context = {
            'uidb64': uidb64,
            'token': token
        }
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, 'les mots de passes ne sont pas identiques')
            return render(request, 'authentication/set-new-password.html', context)

        if len(password) < 6:
            messages.error(request, 'le mot de passe doit contenir 6 caractères minimum')
            return render(request, 'authentication/set-new-password.html', context)
            

        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password)
            user.save()
            messages.success(request, 'Votre mot de passe a bien été mis à jour, vous pouvez vous connecter')

            return redirect('login')

        except Exception as identifier:
            messages.info(request, 'OOps un probème est survenu, veuillez réessayer !!')
            return render(request, 'authentication/set-new-password.html', context)

class ContactView(View):
    def get(self, request):
        return render(request, 'authentication/contact.html')

    def post(self, request):
        nom = request.POST['nom']
        email = request.POST['email']
        sujet = request.POST['sujet']
        message = request.POST['message']

        context = {
            'fieldValues': request.POST
        }

        if not User.objects.filter(email=email).exists():
                messages.error(request, 'Email {0} associé à aucun compte'.format(email))
                return render(request, 'authentication/contact.html', context)

        email = EmailMessage(
                    sujet,
                    message,
                    email,
                    ['axelmouele4591@gmail.com'],
                )
                
        EmailThread(email).start()            
        messages.success(request, 'Votre message a été bien reçu .')
                
        return render(request, 'authentication/contact.html', context)



