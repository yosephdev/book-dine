from django.shortcuts import render


def custom_404_view(request, exception):  
    """ Error Handler 404 - Page Not Found """   
    return render(request, 'errors/404.html', status=404)

def custom_500_view(request):
    """ Error Handler 500 - Server Error """
    return render(request, 'errors/500.html', status=500)
