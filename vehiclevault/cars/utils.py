from cars.models import ActivityLog

def log_activity(user, action_type, description):
    """
    Utility function to log user actions for the Executive Activity Stream.
    """
    if user.is_authenticated:
        ActivityLog.objects.create(
            user=user,
            action_type=action_type,
            description=description
        )
