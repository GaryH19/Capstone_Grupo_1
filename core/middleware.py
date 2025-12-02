from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class NoCacheMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if request.user.is_authenticated:
            response['Cache-Control'] = "no-cache, no-store, must-revalidate, max-age=0"
            response['Pragma'] = "no-cache"
            response['Expires'] = "0"

        return response
    
    
class ForceChangePasswordMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            
            es_temporal = getattr(request.user, 'es_clave_temporal', False)

            if es_temporal:
                try:
                    path_force = reverse('force_change_password') 
                    path_logout = reverse('logout')
                except:
                    path_force = None
                    path_logout = None

                current_path = request.path

                if current_path != path_force and current_path != path_logout:
                    
                    if not current_path.startswith('/static/') and not current_path.startswith('/media/'):

                        return redirect('force_change_password')

        response = self.get_response(request)
        return response
