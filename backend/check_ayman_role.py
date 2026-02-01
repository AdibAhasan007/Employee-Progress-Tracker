from core.models import User

# Check Ayman's role
ayman = User.objects.filter(username='Ayman').first()
if ayman:
    print(f"Username: {ayman.username}")
    print(f"Role: {ayman.role}")
else:
    print("User 'Ayman' not found")

# List all users
print("\nAll Users:")
for user in User.objects.all():
    print(f"{user.username} -> {user.role}")
