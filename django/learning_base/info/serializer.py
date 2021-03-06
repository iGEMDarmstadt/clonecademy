"""
Serializers for the information type questions
"""
from re import compile

from rest_framework import serializers
from .models import InformationYoutube, InformationText


class InformationTextSerializer(serializers.ModelSerializer):
    """
    The serializer for information text type questions.
    @author: Claas Voelcker
    """

    class Meta:
        model = InformationText
        fields = ('text_field', 'image')

    def create(self, validated_data):
        """
        creates a InformationText from validated data
        :param validated_data: the data for the new db entry
        """
        question = InformationText(**validated_data)
        question.module = validated_data['module']
        question.save()


class InformationYoutubeSerializer(serializers.ModelSerializer):
    """
    The serializer for information video type questions.
    @author: Claas Voelcker
    """

    # ID extraction pattern
    pattern = compile(
        r'(?:http(?:s)?)?:\/\/(?:www\.)?(?:youtu\.be|youtube\.com)?\/(?:watch\?v=|embed\/)?(.*)')

    class Meta:
        model = InformationYoutube
        fields = ('text_field', 'url')

    def create(self, validated_data):
        """
        Creates the object. Takes a valid youtube url and extracts the video
        id. This makes it possible to
        :param validated_data: the JSON containing all data
        :return: True for a valid serialization
        """
        question = InformationYoutube(**validated_data)
        question.url = self.pattern.findall(validated_data['url'])[0]
        question.module = validated_data['module']
        question.save()
        return True
