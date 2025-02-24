import random
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User  # Django'nun built-in User modeli
from .models import Word,Points


def get_current_player(request):
    # request.user üzerinden kontrol yapıyoruz.
    return request.user if request.user.is_authenticated else None

def home(request):
    user = get_current_player(request)
    scoreboard_data = Points.objects.select_related('user').order_by('-score')
    return render(request, 'game/home.html', {
        "player": user,
        "points": scoreboard_data
    })



def login_view(request):
    # Eğer kullanıcı zaten oturum açmışsa (örneğin admin), önce çıkış yapalım.
    if request.user.is_authenticated:
        logout(request)
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # Django session'ı otomatik yönetir.
            messages.success(request, f"Hoş geldin, {user.username}!")
            return redirect('game')
        else:
            messages.error(request, "Kullanıcı adı veya şifre yanlış.")
    return render(request, 'game/login.html', {"player": get_current_player(request)})

def logout_view(request):
    logout(request)
    return redirect('home')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        if not username or not password:
            messages.error(request, "Kullanıcı adı ve şifre zorunludur.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Bu kullanıcı adı zaten alınmış.")
        else:
            new_user = User(username=username)
            new_user.set_password(password)  # Şifrenin hash'lenmesi burada gerçekleşiyor.
            new_user.save()
            messages.success(request, "Kayıt başarılı, lütfen giriş yapın.")
            return redirect('login')
    return render(request, 'game/register.html', {"player": get_current_player(request)})


def add_word(request):
    user = get_current_player(request)
    if request.method == 'POST':
        word_text = request.POST.get('word', '').strip().lower()
        if word_text:
            if Word.objects.filter(text=word_text).exists():
                messages.error(request, "Bu kelime zaten var.")
            else:
                Word.objects.create(text=word_text)
                messages.success(request, "Kelime başarıyla eklendi.")
                return redirect('add_word')
        else:
            messages.error(request, "Lütfen bir kelime girin.")
    return render(request, 'game/add_word.html', {"player": user})

import random
import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Word, Points

def get_current_player(request):
    return request.user if request.user.is_authenticated else None

import random
import re
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Word, Points

def get_current_player(request):
    return request.user if request.user.is_authenticated else None

def game_view(request):
    user = get_current_player(request)
    if not user:
        return redirect('login')

    # Eğer henüz bir kelime seçilmemişse, rastgele bir kelime seç ve oturumda sakla.
    if "secret_word_id" not in request.session:
        words = list(Word.objects.all())
        if not words:
            return render(request, "game/game.html", {
                "error": "Veritabanında kelime bulunmuyor. Lütfen kelime ekleyin.",
                "player": user
            })
        chosen = random.choice(words)
        request.session["secret_word_id"] = chosen.id
        request.session["correct_guesses"] = []
        request.session["wrong_count"] = 0

    secret_word_obj = Word.objects.get(id=request.session["secret_word_id"])
    secret_word = secret_word_obj.text

    # Seçilen kelimeye ait ipucunu al (varsa)
    try:
        hint_text = secret_word_obj.hint.hint_text
    except Exception:
        hint_text = ""

    correct_guesses = request.session.get("correct_guesses", [])
    wrong_count = request.session.get("wrong_count", 0)
    message = request.session.pop("message", "")

    if request.method == 'POST':
        guess = request.POST.get('guess', '').lower().strip()
        full_guess = request.POST.get('full_word', '').lower().strip()

        # Sadece a-z arası harf için kontrol (guess)
        if guess and not re.match("^[a-z]$", guess):
            messages.error(request, "Lütfen geçerli bir harf giriniz (sadece a-z).")
            return redirect("game")
        # full_guess için sadece a-z ve boşluk kontrolü
        if full_guess and not re.match("^[a-z\s]+$", full_guess):
            messages.error(request, "Lütfen geçerli bir kelime giriniz (sadece a-z ve boşluk).")
            return redirect("game")

        if full_guess:
            if full_guess == secret_word:
                message = f"Kazandınız! Kelime: {secret_word}"
                points, created = Points.objects.get_or_create(user=user)
                points.score += 5
                points.save()
                request.session["message"] = message
                # Yeni oyuna geçmek için oturum bilgilerini temizle
                del request.session["secret_word_id"]
                del request.session["correct_guesses"]
                del request.session["wrong_count"]
                return redirect("game")
            else:
                wrong_count += 1
                request.session["wrong_count"] = wrong_count
        elif guess and len(guess) == 1:
            if guess in secret_word:
                if guess not in correct_guesses:
                    correct_guesses.append(guess)
                    request.session["correct_guesses"] = correct_guesses
            else:
                wrong_count += 1
                request.session["wrong_count"] = wrong_count

        if all(letter in correct_guesses or letter == " " for letter in secret_word):
            message = f"Kazandınız! Kelime: {secret_word}"
            points, created = Points.objects.get_or_create(user=user)
            points.score += 5
            points.save()
            request.session["message"] = message
            del request.session["secret_word_id"]
            del request.session["correct_guesses"]
            del request.session["wrong_count"]
        elif wrong_count >= 6:
            message = f"Kaybettiniz! Kelime: {secret_word}"
            request.session["message"] = message
            del request.session["secret_word_id"]
            del request.session["correct_guesses"]
            del request.session["wrong_count"]

        return redirect("game")

    scoreboard_data = Points.objects.select_related('user').order_by('-score')

    return render(request, "game/game.html", {
        "player": user,
        "secret_word": secret_word,
        "correct_guesses": correct_guesses,
        "wrong_count": wrong_count,
        "message": message,
        "points": scoreboard_data,
        "hint": hint_text,
    })





def scoreboard(request):
    user = get_current_player(request)
    points = Points.objects.order_by("-score")
    return render(request, "game/scoreboard.html", {
        "points": points,
        "player": user
    })
