"""
LLM Processor Module
Handles interaction with various LLM providers (OpenAI, Anthropic, local models)
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class LLMProcessor:
    """Processes content using various LLM providers"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize LLM processor

        Args:
            config: LLM configuration with provider, model, api_key, system_prompt
        """
        self.config = config
        self.provider = config.get('provider', 'openai')
        self.model = config.get('model', 'gpt-4-turbo-preview')
        self.api_key = config.get('api_key', '')
        self.system_prompt = config.get('system_prompt', 'You are a helpful assistant.')

        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the appropriate LLM client"""
        try:
            if self.provider == 'openai':
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                logger.info(f"Initialized OpenAI client with model: {self.model}")

            elif self.provider == 'anthropic':
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key)
                logger.info(f"Initialized Anthropic client with model: {self.model}")
            
            elif self.provider == 'kimi':
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key, base_url="https://api.moonshot.cn/v1")
                logger.info(f"Initialized Kimin client with model: {self.model}")

            elif self.provider == 'local':
                # For local models (e.g., Ollama, LM Studio)
                from openai import OpenAI
                # Assumes local server compatible with OpenAI API
                base_url = self.config.get('base_url', 'http://localhost:11434/v1')
                self.client = OpenAI(api_key='local', base_url=base_url)
                logger.info(f"Initialized local LLM client: {base_url}")

            else:
                raise ValueError(f"Unknown LLM provider: {self.provider}")

        except Exception as e:
            logger.error(f"Error initializing LLM client: {e}")
            self.client = None

    def process(self, content: str, llm_config: Optional[Dict[str, Any]] = None) -> str:
        """
        Process content with LLM

        Args:
            content: Markdown content to process
            llm_config: Optional override config

        Returns:
            LLM response as string
        """
        if not self.client:
            return "Error: LLM client not initialized. Please check your configuration."

        # Use override config if provided
        config = llm_config or self.config
        system_prompt = config.get('system_prompt', self.system_prompt)

        try:
            if self.provider == 'openai' or self.provider == 'local':
                return self._process_openai(content, system_prompt, config)
            elif self.provider == 'anthropic':
                return self._process_anthropic(content, system_prompt, config)
            else:
                return f"Error: Unknown provider {self.provider}"

        except Exception as e:
            logger.error(f"Error processing with LLM: {e}", exc_info=True)
            return f"Error processing content: {str(e)}"

    def _process_openai(self, content: str, system_prompt: str, config: Dict[str, Any]) -> str:
        """Process with OpenAI API"""
        try:
            # Truncate content if too long (max 100k chars)
            if len(content) > 100000:
                content = content[:100000] + "\n\n[Content truncated...]"

            response = self.client.chat.completions.create(
                model=config.get('model', self.model),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Please analyze the following web content:\n\n{content}"}
                ],
                temperature=config.get('temperature', 0.7),
                max_tokens=config.get('max_tokens', 4000)
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return f"Error calling OpenAI API: {str(e)}"

    def _process_anthropic(self, content: str, system_prompt: str, config: Dict[str, Any]) -> str:
        """Process with Anthropic API"""
        try:
            # Truncate content if too long
            if len(content) > 100000:
                content = content[:100000] + "\n\n[Content truncated...]"

            response = self.client.messages.create(
                model=config.get('model', self.model),
                max_tokens=config.get('max_tokens', 4000),
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Please analyze the following web content:\n\n{content}"
                    }
                ]
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return f"Error calling Anthropic API: {str(e)}"


class MockLLMProcessor:
    """Mock LLM processor for testing without API keys"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        logger.info("Initialized Mock LLM Processor (for testing)")

    def process(self, content: str, llm_config: Optional[Dict[str, Any]] = None) -> str:
        """Return a mock response"""
        lines = content.split('\n')
        title = "Unknown"
        url = "Unknown"

        for line in lines[:10]:
            if line.startswith('# '):
                title = line[2:].strip()
            elif 'URL:' in line:
                url = line.split('URL:')[-1].strip()

        return f"""# Summary

This is a mock LLM response for testing purposes.

## Page Information
- **Title:** {title}
- **URL:** {url}

## Analysis
This webpage contains {len(content)} characters of content. In a real scenario, an LLM would provide:

1. **Summary**: A concise overview of the main topics and key points
2. **Key Insights**: Important information extracted from the content
3. **Structure**: How the content is organized
4. **Recommendations**: Suggestions for further reading or action

## Mock Features
Since this is a mock processor, no actual API calls are being made. Configure your API keys in the config to enable real LLM processing.

### Supported Providers
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Local models (Ollama, LM Studio)
"""
