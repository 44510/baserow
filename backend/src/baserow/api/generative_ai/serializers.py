from rest_framework import serializers


class GenerativeAIModelsSerializer(serializers.Serializer):
    models = serializers.ListField(
        required=False,
        child=serializers.CharField(),
        help_text="The models that are enabled for this AI type.",
    )


class OpenAISettingsSerializer(GenerativeAIModelsSerializer):
    api_key = serializers.CharField(
        allow_blank=True,
        required=False,
        help_text="The OpenAI API key that is used to authenticate with the OpenAI API.",
    )
    organization = serializers.CharField(
        allow_blank=True,
        required=False,
        help_text="The organization that the OpenAI API key belongs to.",
    )


class OllamaSettingsSerializer(GenerativeAIModelsSerializer):
    host = serializers.CharField(
        allow_blank=True,
        required=False,
        help_text="The host that is used to authenticate with the Ollama API.",
    )
