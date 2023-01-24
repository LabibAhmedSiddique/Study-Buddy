from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q 
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages  
from .models import Room, Topic ,Massage
from .forms import RoomForm
# rooms = [
#     {'id': 1, 'name': 'learn django'},
#     {'id': 2, 'name': 'learn python'},
#     {'id': 3, 'name': 'front end dev'},
# ]


def loginPage(request):
    page ='login'
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        username=request.POST.get('username').lower()
        password=request.POST.get('password')
        try:
            user=User.objects.get(username=username)
        except:
            messages.error(request, 'User Not Found.')
                

        user=authenticate(request, username=username,password=password)
        
        if user is not None:
            login(request, user)
            return redirect('index') 
        else:
            messages.error(request, 'User Not Found.')

    context = {'page':page}
    return render(request, 'polls/login-register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('index')

def registerUser(request):
    page ='register'
    form =UserCreationForm()
    if request.method == 'POST':
        form =UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username=user.username.lower()
            user.save()
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Something went wrong.')
    
    return render( request,'polls/login-register.html', {'form':form})


def index(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(Q(topic__name__icontains=q)
                                | Q(name__icontains=q)
                                | Q(description__icontains=q))
    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages =Massage.objects.filter(Q(room__topic__name__icontains=q))
    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count, 'room_messages':room_messages} 
    return render(request, 'polls/home.html', context)
    


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.massage_set.all().order_by('-created')
    participents =room.particpents.all()
    if request.method =="POST":
        message=Massage.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.particpents.add(request.user)
        return redirect('room', pk=room.id)
    context = {'room': room,'room_messages':room_messages,'participents':participents}        
    return render(request, 'polls/rooms.html', context)

def userProfile(request, pk):
    user=User.objects.get(id=pk)
    rooms=user.room_set.all()
    room_massages=user.massage_set.all()
    topics=Topic.objects.all()
    context={'user':user, 'rooms':rooms ,'room_massages':room_massages ,'topics':topics}
    return render(request, 'polls/profile.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid:
            room =form.save(commit=False)
            room.host=request.user
            room.save()
            return redirect('index')
    context = {'form': form}
    return render(request, 'polls/room_form.html', context)
    pass

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    if request.user != room.host:
        return HttpResponse('You are not allowerd here')

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid:
            form.save()
            return redirect('index')
    context = {'form': form}
    return render(request, 'polls/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('You are not allowerd here')

    if request.method == 'POST':
        room.delete()
        return redirect('index')

    return render(request, 'polls/delete.html', {'obj': room})

def deleteMessege(request, pk):
    message = Massage.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse('You are not allowerd here')

    if request.method == 'POST':
        message.delete()
        return redirect('index')

    return render(request, 'polls/delete.html', {'obj': message})