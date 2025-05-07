import unittest
from unittest.mock import patch, MagicMock
from app.utils.ai_services import (
    validate_api_key, 
    AIProvider, 
    AIServiceError,
    get_available_models
)

class TestAIServices(unittest.TestCase):
    """Test cases for AI services functionality."""
    
    def test_validate_api_key(self):
        """Test API key validation for different providers."""
        # OpenAI - should start with sk-
        self.assertTrue(validate_api_key(AIProvider.OPENAI.value, "sk-abcdefghijklmnopqrstuvwxyz"))
        self.assertFalse(validate_api_key(AIProvider.OPENAI.value, "bad-key"))
        
        # Google - should be longer than 20 chars
        self.assertTrue(validate_api_key(AIProvider.GOOGLE.value, "abcdefghijklmnopqrstuvwxyz"))
        self.assertFalse(validate_api_key(AIProvider.GOOGLE.value, "short"))
        
        # Empty keys should fail for any provider
        self.assertFalse(validate_api_key(AIProvider.OPENAI.value, ""))
        self.assertFalse(validate_api_key(AIProvider.GOOGLE.value, ""))
        self.assertFalse(validate_api_key(AIProvider.ANTHROPIC.value, ""))
    
    def test_get_available_models_no_api_key(self):
        """Test getting available models without API key (should use predefined list)."""
        models = get_available_models(AIProvider.OPENAI.value)
        
        # Should return the predefined models
        self.assertTrue(len(models) > 0)
        self.assertIn("id", models[0])
        self.assertIn("name", models[0])
        self.assertIn("context_window", models[0])
    
    @patch('app.utils.ai_services.openai.models.list')
    def test_get_available_models_with_api_key(self, mock_list):
        """Test getting available models with a valid API key."""
        # Mock the OpenAI models.list response
        mock_model = MagicMock()
        mock_model.id = "gpt-4"
        mock_response = MagicMock()
        mock_response.data = [mock_model]
        mock_list.return_value = mock_response
        
        models = get_available_models(AIProvider.OPENAI.value, "sk-valid-key")
        
        # Should have at least one model
        self.assertTrue(len(models) > 0)
        
        # The mock was called
        mock_list.assert_called_once()

    @patch('app.utils.ai_services.openai.models.list')
    def test_get_available_models_api_error(self, mock_list):
        """Test handling API errors when fetching models."""
        # Make the API call fail
        mock_list.side_effect = Exception("API Error")
        
        # Should fall back to predefined models
        models = get_available_models(AIProvider.OPENAI.value, "sk-valid-key")
        
        # Should still return models from the predefined list
        self.assertTrue(len(models) > 0)
        self.assertIn("id", models[0])
        self.assertIn("name", models[0])

if __name__ == "__main__":
    unittest.main() 