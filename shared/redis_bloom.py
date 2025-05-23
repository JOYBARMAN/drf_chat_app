from django_redis import get_redis_connection

# Get the default Redis connection from settings
redis_client = get_redis_connection("default")

# Use the RedisBloom extension
bloom = redis_client.bf()


# Add user to Bloom filter
def add_to_bloom_filter(username=None, email=None):
    # Adding username to the filter
    if username:
        bloom.add("user_filter", username)

    # Adding email to the filter
    if email:
        bloom.add("email_filter", email)


def check_username_in_bloom_filter(username: str):
    # Check if username exists in the Bloom filter
    return bloom.exists("user_filter", username)


def check_email_in_bloom_filter(email: str):
    # Check if email exists in the Bloom filter
    return bloom.exists("email_filter", email)
