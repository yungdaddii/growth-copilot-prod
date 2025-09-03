"""Debug endpoint for Firebase configuration."""

from fastapi import APIRouter
import os
import json

router = APIRouter()

@router.get("/debug/firebase-env")
async def debug_firebase_env():
    """Debug endpoint to check Firebase environment variable."""
    
    firebase_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON", "")
    
    # Basic checks
    result = {
        "has_env_var": bool(firebase_json),
        "length": len(firebase_json) if firebase_json else 0,
        "starts_with": firebase_json[:50] if firebase_json else None,
        "ends_with": firebase_json[-50:] if firebase_json else None,
        "has_braces": firebase_json.startswith("{") and firebase_json.endswith("}") if firebase_json else False,
    }
    
    # Try to parse
    try:
        parsed = json.loads(firebase_json)
        result["parse_success"] = True
        result["has_type"] = "type" in parsed
        result["has_project_id"] = "project_id" in parsed
        result["has_private_key"] = "private_key" in parsed
        result["project_id"] = parsed.get("project_id")
        
        # Check private key format
        private_key = parsed.get("private_key", "")
        result["private_key_starts"] = private_key[:30] if private_key else None
        result["private_key_has_newlines"] = "\\n" in private_key
        result["private_key_has_actual_newlines"] = "\n" in private_key
        
    except json.JSONDecodeError as e:
        result["parse_success"] = False
        result["parse_error"] = str(e)
        
        # Try to identify the issue
        if firebase_json.startswith('"') and firebase_json.endswith('"'):
            result["issue"] = "JSON is wrapped in quotes"
            # Try to unwrap and parse
            try:
                unwrapped = firebase_json[1:-1].replace('\\"', '"')
                parsed = json.loads(unwrapped)
                result["unwrap_success"] = True
            except:
                result["unwrap_success"] = False
    
    return result