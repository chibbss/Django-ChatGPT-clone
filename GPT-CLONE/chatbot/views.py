from django.shortcuts import render, redirect
from django.http import JsonResponse
import openai
from django.contrib import auth
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from .models import Chat
from django.utils import timezone

openai_api_key = 'your_openai_api_key'
openai.api_key = openai_api_key

# create openai interaction function
def ask_openai(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages = [
                {'role': 'system', 'content': 'You are a fitness and nutrition expert and coach.'},
                {'role': 'user', 'content': message},
            ]
        )

        answer = response.choices[0].message.content.strip()
        return answer

    except openai.error.OpenAIError as e:
        if "gpt-4" in str(e):
            # This specific error indicates that the quota is finished for the model
            return "Hey, it seems like my ability to respond is temporarily limited. Is your quota finished?"
        else:
            # Handle other OpenAI errors
            error_message = str(e)
            print(f"OpenAI Error: {error_message}")
            return f"An error occurred: {error_message}. Please try again later."



# Create your views here.
def chatbot(request):
    # to show the user chat history
    chats = Chat.objects.filter(user=request.user)

    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_openai(message)

        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'chatbot.html', {'chats': chats})

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        # authenticate the user ie check if user exists
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = "Oops! we can't seem to find this user. Invalid username or password."
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                # logs user in automatically if registered
                auth.login(request, user)
                return redirect('chatbot')
            except IntegrityError as e:
                error_message = 'A user with this username or email already exists.'
            except Exception as e:
                error_message = 'Oops! We ran into some trouble creating your account, try again.'
            return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = 'Passwords do not match.'
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                # logs user in automatically if registered
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message = 'Oops! We ran into some trouble creating your account, try again.'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = 'Passwords do not match.'
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('login') 
