from django.shortcuts import redirect , render

from django.http import HttpResponse, JsonResponse
def redirect_view1(request):
    response = redirect('cr/')
    return response
def for_task1(request):
    return HttpResponse('<h1>Congratulations ! you have succesfully submitted task 1</h1> ')

def city_view(request):
    return render(request,'civifest.html')

def form_view(request):
    return render(request,'form_event.html')


def health_check(request):
    return JsonResponse({'status': 'ok'})
