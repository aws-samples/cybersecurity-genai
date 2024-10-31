# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from enum import StrEnum
from typing import NamedTuple



# Constants for model names
AMAZON_TITAN_PREMIER = 'amazon.titan-text-premier-v1:0'
AMAZON_TITAN_LITE = 'amazon.titan-text-lite-v1'
AMAZON_TITAN_EXPRESS = 'amazon.titan-text-express-v1'
AI21_J2_MID = 'ai21.j2-mid-v1'
AI21_J2_ULTRA = 'ai21.j2-ultra-v1'
ANTHROPIC_CLAUDE3_SONNET = 'anthropic.claude-3-sonnet-20240229-v1:0'
ANTHROPIC_CLAUDE3_HAIKU = 'anthropic.claude-3-haiku-20240307-v1:0'
ANTHROPIC_CLAUDE3_OPUS = 'anthropic.claude-3-opus-20240307-v1:0'
COHERE_COMMAND_R = 'cohere.command-r-v1:0'
COHERE_COMMAND_R_PLUS = 'cohere.command-r-plus-v1:0'
META_LLAMA3_8B_INSTRUCT = 'meta.llama3-8b-instruct-v1:0'
META_LLAMA3_70B_INSTRUCT = 'meta.llama3-70b-instruct-v1:0'
MISTRAL_7B_INSTRUCT = 'mistral.mistral-7b-instruct-v0:2'
MISTRAL_MIXTRAL_8X7B_INSTRUCT = 'mistral.mixtral-8x7b-instruct-v0:1'
MISTRAL_LARGE = 'mistral.mistral-large-2402-v1:0'
MISTRAL_SMALL = 'mistral.mistral-small-2402-v1:0'

class ModelMetadata(NamedTuple):
    """
    Metadata for a Foundation Model, including its support for various features.
    """
    system_message_support: bool
    message_history_support: bool
    tool_support: bool
    image_support: bool

class Models(StrEnum):
    """
    This is a subset of Foundation Models available on Amazon Bedrock available to use with this helper.
    More information about these models, and all Bedrock models can be found here: 
    https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html
    """
    AMAZON_TITAN_PREMIER = AMAZON_TITAN_PREMIER
    AMAZON_TITAN_LITE = AMAZON_TITAN_LITE
    AMAZON_TITAN_EXPRESS = AMAZON_TITAN_EXPRESS
    AI21_J2_MID = AI21_J2_MID
    AI21_J2_ULTRA = AI21_J2_ULTRA
    ANTHROPIC_CLAUDE3_SONNET = ANTHROPIC_CLAUDE3_SONNET
    ANTHROPIC_CLAUDE3_HAIKU = ANTHROPIC_CLAUDE3_HAIKU
    ANTHROPIC_CLAUDE3_OPUS = ANTHROPIC_CLAUDE3_OPUS
    COHERE_COMMAND_R = COHERE_COMMAND_R
    COHERE_COMMAND_R_PLUS = COHERE_COMMAND_R_PLUS
    META_LLAMA3_8B_INSTRUCT = META_LLAMA3_8B_INSTRUCT
    META_LLAMA3_70B_INSTRUCT = META_LLAMA3_70B_INSTRUCT
    MISTRAL_7B_INSTRUCT = MISTRAL_7B_INSTRUCT
    MISTRAL_MIXTRAL_8x7B_INSTRUCT = MISTRAL_MIXTRAL_8X7B_INSTRUCT
    MISTRAL_LARGE = MISTRAL_LARGE
    MISTRAL_SMALL = MISTRAL_SMALL
    
    @property
    def metadata(self):
        """
        Returns the features supported by the mode.
        """
        return MODEL_METADATA[self]
    
MODEL_METADATA = {
    Models.AMAZON_TITAN_PREMIER: ModelMetadata(False, True, False, False),
    Models.AMAZON_TITAN_LITE: ModelMetadata(False, True, False, False),
    Models.AMAZON_TITAN_EXPRESS: ModelMetadata(False, True, False, False),
    Models.AI21_J2_MID: ModelMetadata(False, False, False, False),
    Models.AI21_J2_ULTRA: ModelMetadata(False, False, False, False),
    Models.ANTHROPIC_CLAUDE3_SONNET: ModelMetadata(True, True, True, True),
    Models.ANTHROPIC_CLAUDE3_HAIKU: ModelMetadata(True, True, True, True),
    Models.ANTHROPIC_CLAUDE3_OPUS: ModelMetadata(True, True, True, True),
    Models.COHERE_COMMAND_R: ModelMetadata(True, True, True, False),
    Models.COHERE_COMMAND_R_PLUS: ModelMetadata(True, True, True, False),
    Models.META_LLAMA3_8B_INSTRUCT: ModelMetadata(True, True, False, False),
    Models.META_LLAMA3_70B_INSTRUCT: ModelMetadata(True, True, False, False),
    Models.MISTRAL_7B_INSTRUCT: ModelMetadata(False, True, True, False),
    Models.MISTRAL_MIXTRAL_8x7B_INSTRUCT: ModelMetadata(False, True, True, False),
    Models.MISTRAL_LARGE: ModelMetadata(True, True, True, False),
    Models.MISTRAL_SMALL: ModelMetadata(True, True, True, False),
}