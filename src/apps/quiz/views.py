from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import QuizForm
import requests
from decouple import config

BITRIX_BASE_URL = config("WEBHOOK_URL")


def send_to_bitrix(title, name, phone, details, consultation_method):
    payload = {
        "fields": {
            "TITLE": title,
            "NAME": name,
            "PHONE": [{"VALUE": phone, "VALUE_TYPE": "WORK"}],
            "COMMENTS": f"{details}\nСпособ консультации: {consultation_method}",
        }
    }
    try:
        response = requests.post(f"{BITRIX_BASE_URL}crm.lead.add.json", json=payload, timeout=10)
        print("Bitrix response:", response.json())
    except Exception as e:
        print("Ошибка Bitrix24:", e)


def home(request):
    return render(request, "home.html")


def family_quiz(request):
    if request.method == "POST":
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save()

            # Отправляем в Bitrix24
            send_to_bitrix(
                title=f"Заявка ({quiz.get_case_type_display()})",
                name=quiz.full_name,
                phone=quiz.phone,
                details=f"Тип дела: {quiz.get_case_type_display()}\nОписание: {quiz.details}",
                consultation_method=quiz.get_consultation_method_display(),
            )

            messages.success(request, "Спасибо! Мы скоро с вами свяжемся.")
            return redirect("quiz-success")
    else:
        form = QuizForm()

    return render(request, "index.html", {"form": form, "title": "Семейные дела"})


def quiz_success(request):
    return render(request, "success.html")
