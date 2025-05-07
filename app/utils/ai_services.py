import requests
import os
import json
from typing import Dict, Any, Optional, List, Tuple
import google.generativeai as genai
import openai
from enum import Enum

class AIProvider(Enum):
    """Supported AI provider options."""
    OPENAI = "OpenAI (ChatGPT)"
    GOOGLE = "Google Gemini"
    NVIDIA = "NVIDIA NIMs"
    OPENROUTER = "OpenRouter"
    ANTHROPIC = "Anthropic Claude"
    COHERE = "Cohere"
    CUSTOM = "Custom API"

# Available models for each provider with their context window size
AVAILABLE_MODELS = {
    AIProvider.OPENAI.value: [
        {"id": "gpt-4o", "name": "GPT-4o", "context_window": 128000, "description": "OpenAI's latest multimodal model with improved capabilities"},
        {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "context_window": 128000, "description": "Latest GPT-4 model with improved capabilities"},
        {"id": "gpt-4", "name": "GPT-4", "context_window": 8192, "description": "OpenAI's powerful large language model"},
        {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "context_window": 16385, "description": "Optimized for chat at a lower cost"}
    ],
    AIProvider.GOOGLE.value: [
        {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "context_window": 1000000, "description": "Google's most powerful model with very large context window"},
        {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash", "context_window": 1000000, "description": "Faster version of Gemini 1.5 with large context"},
        {"id": "gemini-pro", "name": "Gemini Pro", "context_window": 32768, "description": "Balanced performance for most tasks"}
    ],
    AIProvider.ANTHROPIC.value: [
        {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "context_window": 200000, "description": "Anthropic's most powerful model"},
        {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet", "context_window": 200000, "description": "Balanced performance and cost"},
        {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku", "context_window": 200000, "description": "Fastest Claude model for quick responses"}
    ],
    AIProvider.NVIDIA.value: [
        {"id": "llama3-70b-instruct", "name": "Llama 3 70B Instruct", "context_window": 8192, "description": "Meta's Llama 3 70B model"},
        {"id": "llama3-8b-instruct", "name": "Llama 3 8B Instruct", "context_window": 8192, "description": "Meta's Llama 3 8B model"}
    ],
    AIProvider.OPENROUTER.value: [
        {"id": "openai/gpt-4o", "name": "OpenAI GPT-4o", "context_window": 128000, "description": "Latest GPT-4 model via OpenRouter"},
        {"id": "anthropic/claude-3-opus", "name": "Anthropic Claude 3 Opus", "context_window": 200000, "description": "Claude 3 Opus via OpenRouter"},
        {"id": "google/gemini-pro", "name": "Google Gemini Pro", "context_window": 32768, "description": "Google's Gemini Pro via OpenRouter"},
        {"id": "meta-llama/llama-3-70b-instruct", "name": "Meta Llama 3 70B", "context_window": 8192, "description": "Llama 3 70B via OpenRouter"}
    ],
    AIProvider.COHERE.value: [
        {"id": "command-r-plus", "name": "Command R+", "context_window": 128000, "description": "Cohere's most powerful model"},
        {"id": "command-r", "name": "Command R", "context_window": 128000, "description": "Balanced performance and cost"},
        {"id": "command-light", "name": "Command Light", "context_window": 4096, "description": "Fast and cost-effective option"}
    ],
    AIProvider.CUSTOM.value: [
        {"id": "custom", "name": "Custom Model", "context_window": 0, "description": "Your custom API endpoint"}
    ]
}

class AIServiceError(Exception):
    """Exception raised for errors in the AI service."""
    pass

def validate_api_key(provider: str, api_key: str) -> bool:
    """
    Validate if the API key is in the correct format for the provider.
    This is a basic validation and doesn't check if the key actually works.
    
    Args:
        provider: The AI provider name
        api_key: The API key to validate
        
    Returns:
        True if the key format is valid, False otherwise
    """
    if not api_key or len(api_key.strip()) < 10:
        return False
        
    # Basic format validation based on provider
    if provider == AIProvider.OPENAI.value:
        return api_key.startswith("sk-")
    elif provider == AIProvider.GOOGLE.value:
        return len(api_key) > 20  # Gemini API keys are long
    elif provider == AIProvider.ANTHROPIC.value:
        return api_key.startswith("sk-")
    elif provider == AIProvider.OPENROUTER.value:
        return api_key.startswith("sk-")
    
    # For other providers, just check if it's not empty
    return bool(api_key.strip())

def get_available_models(provider: str, api_key: str = None) -> List[Dict[str, Any]]:
    """
    Get available models for a given provider, either from local list or by API call
    
    Args:
        provider: The AI provider name
        api_key: Optional API key to fetch models via API
        
    Returns:
        List of available models with their details
    """
    # If API key is provided, try to fetch models from API
    if api_key and validate_api_key(provider, api_key):
        try:
            if provider == AIProvider.OPENAI.value:
                return get_openai_models(api_key)
            elif provider == AIProvider.GOOGLE.value:
                return get_gemini_models(api_key)
            elif provider == AIProvider.OPENROUTER.value:
                return get_openrouter_models(api_key)
        except Exception as e:
            # If API call fails, fall back to local list
            print(f"Error fetching models from API: {e}")
    
    # Return locally defined models
    return AVAILABLE_MODELS.get(provider, [])

def get_openai_models(api_key: str) -> List[Dict[str, Any]]:
    """Fetch available models from OpenAI API"""
    openai.api_key = api_key
    try:
        models = openai.models.list()
        model_list = []
        for model in models.data:
            # Filter for chat models only
            if "gpt" in model.id and any(x in model.id for x in ["gpt-4", "gpt-3.5"]):
                model_info = {
                    "id": model.id,
                    "name": model.id.replace("gpt-", "GPT-").replace("-", " ").title(),
                    "context_window": 0,  # OpenAI API doesn't provide this info directly
                    "description": "OpenAI model"
                }
                model_list.append(model_info)
        return model_list
    except Exception as e:
        # Fall back to predefined models
        return AVAILABLE_MODELS.get(AIProvider.OPENAI.value, [])

def get_gemini_models(api_key: str) -> List[Dict[str, Any]]:
    """Fetch available models from Google Gemini API"""
    genai.configure(api_key=api_key)
    try:
        models = genai.list_models()
        model_list = []
        for model in models:
            if "gemini" in model.name:
                model_info = {
                    "id": model.name,
                    "name": model.name.replace("-", " ").title(),
                    "context_window": 0,
                    "description": "Google Gemini model"
                }
                model_list.append(model_info)
        return model_list
    except Exception as e:
        # Fall back to predefined models
        return AVAILABLE_MODELS.get(AIProvider.GOOGLE.value, [])

def get_openrouter_models(api_key: str) -> List[Dict[str, Any]]:
    """Fetch available models from OpenRouter API"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers=headers
        )
        response.raise_for_status()
        result = response.json()
        
        model_list = []
        for model in result.get("data", []):
            model_info = {
                "id": model.get("id"),
                "name": model.get("name", model.get("id", "Unknown")),
                "context_window": model.get("context_length", 0),
                "description": f"{model.get('description', 'Model from OpenRouter')}"
            }
            model_list.append(model_info)
        return model_list
    except Exception as e:
        # Fall back to predefined models
        return AVAILABLE_MODELS.get(AIProvider.OPENROUTER.value, [])

def analyze_resume_with_ai(
    resume_text: str, 
    provider: str, 
    api_key: str, 
    system_prompt: str,
    model_id: str = None,
    extracted_skills: Optional[Dict[str, List[str]]] = None,
    extracted_sections: Optional[Dict[str, str]] = None,
    max_tokens: int = 1000
) -> Dict[str, Any]:
    """
    Send resume text to the selected AI provider for analysis.
    
    Args:
        resume_text: The extracted resume text
        provider: The AI provider to use
        api_key: The API key for the provider
        system_prompt: The system prompt to guide the AI
        model_id: Optional specific model ID to use
        extracted_skills: Optional dictionary of extracted skills
        extracted_sections: Optional dictionary of extracted resume sections
        max_tokens: Maximum tokens for the response
        
    Returns:
        Dictionary containing the AI analysis and any relevant metadata
    """
    if not validate_api_key(provider, api_key):
        raise AIServiceError("Invalid API key format for the selected provider.")
    
    # Prepare the full prompt with the resume text and extracted info
    full_prompt = f"Resume Text:\n\n{resume_text}\n\n"
    
    if extracted_skills:
        tech_skills = ", ".join(extracted_skills.get("technical_skills", []))
        soft_skills = ", ".join(extracted_skills.get("soft_skills", []))
        full_prompt += f"Extracted Technical Skills: {tech_skills}\n\n"
        full_prompt += f"Extracted Soft Skills: {soft_skills}\n\n"
    
    if extracted_sections:
        full_prompt += "Extracted Resume Sections:\n"
        for section, content in extracted_sections.items():
            # Add only the first 200 chars of each section to avoid very long prompts
            content_preview = content[:200] + "..." if len(content) > 200 else content
            full_prompt += f"{section.upper()}: {content_preview}\n\n"
    
    user_prompt = """
    Please analyze this resume and provide the following:
    
    1. Overall Resume Assessment (strength/quality)
    2. Key Strengths
    3. Areas for Improvement 
    4. Suggestions to enhance impact
    5. Recommended action items in order of priority
    
    Focus on content, impact, and relevance rather than formatting.
    """
    
    try:
        if provider == AIProvider.OPENAI.value:
            return analyze_with_openai(api_key, system_prompt, full_prompt, user_prompt, max_tokens, model_id)
        elif provider == AIProvider.GOOGLE.value:
            return analyze_with_gemini(api_key, system_prompt, full_prompt, user_prompt, max_tokens, model_id)
        elif provider == AIProvider.OPENROUTER.value:
            return analyze_with_openrouter(api_key, system_prompt, full_prompt, user_prompt, max_tokens, model_id)
        elif provider == AIProvider.ANTHROPIC.value:
            return analyze_with_anthropic(api_key, system_prompt, full_prompt, user_prompt, max_tokens, model_id)
        elif provider == AIProvider.COHERE.value:
            return analyze_with_cohere(api_key, system_prompt, full_prompt, user_prompt, max_tokens, model_id)
        elif provider == AIProvider.NVIDIA.value:
            return analyze_with_nvidia(api_key, system_prompt, full_prompt, user_prompt, max_tokens, model_id)
        elif provider == AIProvider.CUSTOM.value:
            return analyze_with_custom_api(api_key, system_prompt, full_prompt, user_prompt, max_tokens)
        else:
            raise AIServiceError(f"Unsupported AI provider: {provider}")
    except Exception as e:
        raise AIServiceError(f"Error analyzing resume with {provider}: {str(e)}")

def analyze_with_openai(api_key: str, system_prompt: str, context: str, user_prompt: str, max_tokens: int, model_id: str = None) -> Dict[str, Any]:
    """Use OpenAI API to analyze the resume."""
    openai.api_key = api_key
    
    # Default model if none specified
    if not model_id:
        model_id = "gpt-4o"
    
    try:
        response = openai.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": context + user_prompt}
            ],
            max_tokens=max_tokens
        )
        
        analysis = response.choices[0].message.content
        
        return {
            "analysis": analysis,
            "provider": "OpenAI",
            "model": response.model,
            "tokens_used": response.usage.total_tokens
        }
    except Exception as e:
        # Try again with gpt-3.5-turbo if the requested model fails
        if model_id != "gpt-3.5-turbo":
            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": context + user_prompt}
                    ],
                    max_tokens=max_tokens
                )
                
                analysis = response.choices[0].message.content
                
                return {
                    "analysis": analysis,
                    "provider": "OpenAI",
                    "model": response.model,
                    "tokens_used": response.usage.total_tokens
                }
            except Exception as fallback_error:
                raise AIServiceError(f"OpenAI API error: {str(fallback_error)}")
        else:
            raise AIServiceError(f"OpenAI API error: {str(e)}")

def analyze_with_gemini(api_key: str, system_prompt: str, context: str, user_prompt: str, max_tokens: int, model_id: str = None) -> Dict[str, Any]:
    """Use Google's Gemini API to analyze the resume."""
    genai.configure(api_key=api_key)
    
    # Default model if none specified
    if not model_id:
        model_id = "gemini-pro"
    
    try:
        model = genai.GenerativeModel(model_id)
        
        # Combine system prompt and user content
        prompt = f"{system_prompt}\n\n{context}{user_prompt}"
        
        response = model.generate_content(prompt, generation_config={
            "max_output_tokens": max_tokens,
            "temperature": 0.4
        })
        
        return {
            "analysis": response.text,
            "provider": "Google Gemini",
            "model": model_id,
            "tokens_used": None  # Gemini doesn't provide token usage info
        }
    except Exception as e:
        raise AIServiceError(f"Gemini API error: {str(e)}")

def analyze_with_anthropic(api_key: str, system_prompt: str, context: str, user_prompt: str, max_tokens: int, model_id: str = None) -> Dict[str, Any]:
    """Use Anthropic Claude API to analyze the resume."""
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01"
    }
    
    # Default model if none specified
    if not model_id:
        model_id = "claude-3-opus-20240229"
    
    data = {
        "model": model_id,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context + user_prompt}
        ]
    }
    
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        result = response.json()
        
        return {
            "analysis": result["content"][0]["text"],
            "provider": "Anthropic Claude",
            "model": result["model"],
            "tokens_used": None  # Claude API doesn't provide token usage in the same way
        }
    except Exception as e:
        raise AIServiceError(f"Anthropic API error: {str(e)}")

def analyze_with_openrouter(api_key: str, system_prompt: str, context: str, user_prompt: str, max_tokens: int, model_id: str = None) -> Dict[str, Any]:
    """Use OpenRouter to access various models."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Default model if none specified
    if not model_id:
        model_id = "openai/gpt-4o"
    
    data = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context + user_prompt}
        ],
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        result = response.json()
        
        return {
            "analysis": result["choices"][0]["message"]["content"],
            "provider": "OpenRouter",
            "model": result["model"],
            "tokens_used": result.get("usage", {}).get("total_tokens")
        }
    except Exception as e:
        raise AIServiceError(f"OpenRouter API error: {str(e)}")

def analyze_with_cohere(api_key: str, system_prompt: str, context: str, user_prompt: str, max_tokens: int, model_id: str = None) -> Dict[str, Any]:
    """Use Cohere API to analyze the resume."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Default model if none specified
    if not model_id:
        model_id = "command-r-plus"
    
    data = {
        "model": model_id,
        "message": context + user_prompt,
        "preamble": system_prompt,
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(
            "https://api.cohere.ai/v1/chat",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        result = response.json()
        
        return {
            "analysis": result["text"],
            "provider": "Cohere",
            "model": model_id,
            "tokens_used": None  # Cohere doesn't provide token usage in the same format
        }
    except Exception as e:
        raise AIServiceError(f"Cohere API error: {str(e)}")

def analyze_with_nvidia(api_key: str, system_prompt: str, context: str, user_prompt: str, max_tokens: int, model_id: str = None) -> Dict[str, Any]:
    """Use NVIDIA NIM API to analyze the resume."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Default model if none specified
    if not model_id:
        model_id = "llama3-70b-instruct"
    
    data = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context + user_prompt}
        ],
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(
            "https://api.nvcf.nvidia.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        result = response.json()
        
        return {
            "analysis": result["choices"][0]["message"]["content"],
            "provider": "NVIDIA NIMs",
            "model": result.get("model", model_id),
            "tokens_used": result.get("usage", {}).get("total_tokens")
        }
    except Exception as e:
        raise AIServiceError(f"NVIDIA API error: {str(e)}")

def analyze_with_custom_api(api_key: str, system_prompt: str, context: str, user_prompt: str, max_tokens: int) -> Dict[str, Any]:
    """Use a custom API endpoint specified by the user."""
    # Extract the endpoint URL and authentication method from the API key string
    # Format expected: "endpoint_url|header_name:header_value"
    try:
        parts = api_key.split('|', 1)
        endpoint_url = parts[0].strip()
        
        headers = {"Content-Type": "application/json"}
        if len(parts) > 1:
            auth_parts = parts[1].split(':', 1)
            header_name = auth_parts[0].strip()
            header_value = auth_parts[1].strip() if len(auth_parts) > 1 else ""
            headers[header_name] = header_value
        
        data = {
            "system_prompt": system_prompt,
            "prompt": context + user_prompt,
            "max_tokens": max_tokens
        }
        
        response = requests.post(
            endpoint_url,
            headers=headers,
            json=data
        )
        response.raise_for_status()
        result = response.json()
        
        # Assume the response has a 'text' or 'content' field
        analysis = result.get("text", result.get("content", result.get("response", str(result))))
        
        return {
            "analysis": analysis if isinstance(analysis, str) else json.dumps(analysis),
            "provider": "Custom API",
            "model": result.get("model", "custom"),
            "tokens_used": None
        }
    except Exception as e:
        raise AIServiceError(f"Custom API error: {str(e)}")

def get_job_match_analysis(
    resume_text: str,
    job_description: str,
    provider: str,
    api_key: str,
    model_id: str = None,
    max_tokens: int = 1000
) -> Dict[str, Any]:
    """
    Compare resume against a job description to evaluate match percentage and gaps.
    
    Args:
        resume_text: The extracted resume text
        job_description: The job description text
        provider: The AI provider to use
        api_key: The API key for the provider
        model_id: Optional specific model ID to use
        max_tokens: Maximum tokens for the response
        
    Returns:
        Dictionary containing the match analysis
    """
    system_prompt = """
    You are an expert ATS (Applicant Tracking System) and career coach. 
    Your task is to analyze how well a resume matches a job description.
    Be detailed, fair, and constructive in your assessment.
    """
    
    user_prompt = f"""
    Please analyze how well this resume matches the job description below.
    
    RESUME:
    {resume_text}
    
    JOB DESCRIPTION:
    {job_description}
    
    Please provide:
    1. Match Score (estimated percentage match)
    2. Key Matching Qualifications
    3. Missing Skills/Requirements
    4. Suggestions to Improve Match
    5. Keywords to add to the resume
    """
    
    # Use the appropriate provider's API
    if provider == AIProvider.OPENAI.value:
        return analyze_with_openai(api_key, system_prompt, "", user_prompt, max_tokens, model_id)
    elif provider == AIProvider.GOOGLE.value:
        return analyze_with_gemini(api_key, system_prompt, "", user_prompt, max_tokens, model_id)
    elif provider == AIProvider.OPENROUTER.value:
        return analyze_with_openrouter(api_key, system_prompt, "", user_prompt, max_tokens, model_id)
    elif provider == AIProvider.ANTHROPIC.value:
        return analyze_with_anthropic(api_key, system_prompt, "", user_prompt, max_tokens, model_id)
    elif provider == AIProvider.COHERE.value:
        return analyze_with_cohere(api_key, system_prompt, "", user_prompt, max_tokens, model_id)
    elif provider == AIProvider.NVIDIA.value:
        return analyze_with_nvidia(api_key, system_prompt, "", user_prompt, max_tokens, model_id)
    elif provider == AIProvider.CUSTOM.value:
        return analyze_with_custom_api(api_key, system_prompt, "", user_prompt, max_tokens)
    else:
        raise AIServiceError(f"Unsupported AI provider: {provider}") 