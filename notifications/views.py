
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import Notification

@login_required
def notification_list(request):
    """List all notifications for the current user"""
    notifications = Notification.objects.filter(user=request.user)
    return render(request, 'notifications/notification_list.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, pk):
    """Mark a specific notification as read and redirect to its link"""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    
    if not notification.is_read:
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
    
    # Redirect to the notification's link if it exists
    if notification.link:
        return redirect(notification.link)
    else:
        return redirect('notifications:notification_list')

@login_required
def mark_all_read(request):
    """Mark all notifications as read for the current user"""
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})
