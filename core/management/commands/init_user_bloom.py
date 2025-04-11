from django.core.management.base import BaseCommand

from core.models import User

from shared.redis_bloom import (
    add_to_bloom_filter,
    check_username_in_bloom_filter,
    check_email_in_bloom_filter,
)


class Command(BaseCommand):
    help = "Initialize Bloom filter with old users"

    def handle(self, *args, **options):
        # Query for users
        users = User.objects.all()

        # Process each old user
        for user in users:
            username = user.username
            email = user.email

            # Check if the user is already in the Bloom filter
            username_exists = check_username_in_bloom_filter(username=username)
            email_exists = check_email_in_bloom_filter(email=email)

            if username_exists or email_exists:
                self.stdout.write(
                    self.style.WARNING(
                        f"User {username} already exists in Bloom filter"
                    )
                )
                continue

            # Add user to the Bloom filter
            add_to_bloom_filter(username=username, email=email)

            self.stdout.write(
                self.style.SUCCESS(
                    f"User:{username} email{email} added to Bloom filter"
                )
            )
