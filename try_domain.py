from app.domain import TaskStatus, check_transition, ValidationError

statuses = list(TaskStatus)
print("=" * 65)
print(f"{'CURRENT STATUS':<15} | {'NEW STATUS':<15} | {'RESULT'}")
print("=" * 65)

for current in statuses:
    for new in statuses:
        try:
            check_transition(current, new)
            result = "✓ ALLOWED"
        except ValidationError:
            result = "✗ DENIED"
        print(f"{current.value:<15} | {new.value:<15} | {result}")

print("=" * 65)
