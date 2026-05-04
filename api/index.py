import json

def handler(request, context):
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "status": "success",
            "message": "Movie Detector API is working"
        })
    }
