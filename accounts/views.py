
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse_lazy

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.is_admin():
            return reverse_lazy('products:admin_dashboard')
        elif user.is_manager():
            return reverse_lazy('products:manager_dashboard')
        else:
            return reverse_lazy('products:team_dashboard')

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})
