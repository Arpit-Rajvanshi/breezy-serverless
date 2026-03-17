"""
main.py — Local development entry point.

This file is NOT used in production (Lambda uses the individual handler modules).
It exists purely for local testing without serverless-offline.

Usage:
    python src/main.py
"""

if __name__ == "__main__":
    import json

    print("=== Breezy ATS Microservice — Local Test Runner ===\n")
    print("This service is designed to run on AWS Lambda via Serverless Framework.")
    print("For local testing, use:\n")
    print("  serverless offline\n")
    print("Then test with curl:")
    print("  curl http://localhost:3000/jobs")
    print("  curl http://localhost:3000/applications?job_id=<your_job_id>")
    print("  curl -X POST http://localhost:3000/candidates \\")
    print('       -H "Content-Type: application/json" \\')
    print('       -d \'{"name":"Jane Doe","email":"jane@example.com","phone":"+911234567890","resume_url":"https://example.com/resume.pdf","job_id":"<your_job_id"}\'')
    print()

    # Quick config sanity check
    try:
        from src.config.settings import get_settings
        settings = get_settings()
        print(f"[OK] Configuration loaded. Company: {settings.breezy_company_id}")
        print(f"[OK] Base URL: {settings.breezy_base_url}")
        print(f"[OK] Log level: {settings.log_level}")
    except EnvironmentError as e:
        print(f"[ERROR] {e}")
