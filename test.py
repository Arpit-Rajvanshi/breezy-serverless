# Create a quick test script
import httpx
from src.handlers.jobs_handler import get_jobs
print(get_jobs({}, None))
