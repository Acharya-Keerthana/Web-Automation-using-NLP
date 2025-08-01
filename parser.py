import re
import json

def parse_response(response):
    """
    Parse Ollama response and extract the most relevant JSON based on context
    """
    try:
        # Find all JSON objects in the response
        json_objects = extract_all_json_objects(response)
        
        if not json_objects:
            print("No JSON objects found in response")
            return None
        
        print(f"🔍 Found {len(json_objects)} JSON objects")
        for i, obj in enumerate(json_objects):
            print(f"  {i+1}: {obj}")
        
        # If only one JSON object, return it
        if len(json_objects) == 1:
            return json_objects[0]
        
        # Multiple JSON objects - pick the most relevant one
        # Look for context clues in the response text
        best_json = select_best_json(response, json_objects)
        
        return best_json
        
    except Exception as e:
        print(" JSON extraction error:", e)
        return None

def extract_all_json_objects(text):
    """Extract all valid JSON objects from text"""
    json_objects = []
    
    # Find all potential JSON objects with proper brace matching
    i = 0
    while i < len(text):
        if text[i] == '{':
            # Found start of JSON object
            brace_count = 0
            start = i
            
            # Find matching closing brace
            while i < len(text):
                if text[i] == '{':
                    brace_count += 1
                elif text[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        # Found complete JSON object
                        json_str = text[start:i+1]
                        try:
                            parsed = json.loads(json_str)
                            json_objects.append(parsed)
                        except json.JSONDecodeError:
                            pass  # Skip invalid JSON
                        break
                i += 1
        else:
            i += 1
    
    return json_objects

def select_best_json(response_text, json_objects):
    """Select the most appropriate JSON object based on context"""
    
    # Look for context indicators in the response text
    response_lower = response_text.lower()
    
    # Score each JSON object
    scored_objects = []
    
    for json_obj in json_objects:
        score = 0
        action = json_obj.get('action', '')
        
        # Check if this JSON appears after relevant context keywords
        json_str = json.dumps(json_obj)
        json_position = response_text.find(json_str)
        
        if json_position > -1:
            # Look at text before this JSON object
            preceding_text = response_text[:json_position].lower()
            
            # Score based on preceding context
            if action == 'fill_booking_form':
                if any(phrase in preceding_text for phrase in ['filling booking', 'booking form', 'for filling']):
                    score += 10
                # Check if it's the last occurrence (usually the actual response)
                if json_position > len(response_text) * 0.5:  # Second half of response
                    score += 5
            
            elif action == 'search_car':
                if any(phrase in preceding_text for phrase in ['searching cars', 'search car', 'for searching']):
                    score += 10
                if json_position > len(response_text) * 0.5:
                    score += 5
            
            # Penalize if it appears in example context
            if any(phrase in preceding_text for phrase in ['example', 'format', 'use only']):
                score -= 5
        
        scored_objects.append((score, json_obj))
    
    # Sort by score and return best match
    scored_objects.sort(key=lambda x: x[0], reverse=True)
    
    print(f" JSON scoring results:")
    for score, obj in scored_objects:
        print(f"  Score {score}: {obj}")
    
    return scored_objects[0][1]  # Return highest scored JSON
