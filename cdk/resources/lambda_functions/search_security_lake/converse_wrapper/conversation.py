# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import copy
from dataclasses import dataclass
from enum import StrEnum
import json
from typing import Dict, List, Union
import boto3

from converse_wrapper.models import Models
from converse_wrapper.vision import ContentVision
from converse_wrapper.tools import Tool, ToolPropertyTypes, ToolProperty, ToolState, ContentToolUse, ContentToolResults



def print_features_table():
    """
    Prints a table of supported features for the converse api.
    Feature support is defined in MODEL_METADATA.
    MODEL_METADATA is updated manually.
    """
    model_width = 40
    system_message_width = 16
    message_history_width = 16
    tool_support_width = 15
    image_support_width = 15
    separator_length = sum([model_width, system_message_width, message_history_width, tool_support_width, image_support_width]) + 5 * 3
    separator_length += 1

    header_format = '| {:<{}} | {:<{}} | {:<{}} | {:<{}} | {:<{}} |'
    header_row = header_format.format('model', model_width,
                                    'sys msg support', system_message_width,
                                    'msg hist support', message_history_width,
                                    'tool support', tool_support_width,
                                    'image support', image_support_width)
    print('-' * separator_length)
    print('boto3 bedrock-runtime converse api feature support matrix')
    print('-' * separator_length)
    print(header_row)
    print('-' * separator_length)

    data_format = '| {:<{}} | {:<{}} | {:<{}} | {:<{}} | {:<{}} |'
    for model in Models:
        metadata = model.metadata
        print(data_format.format(str(model), model_width,
                                str(metadata.system_message_support), system_message_width,
                                str(metadata.message_history_support), message_history_width,
                                str(metadata.tool_support), tool_support_width,
                                str(metadata.image_support), image_support_width))
    print('-' * separator_length)
    return

class Roles(StrEnum):
    """
    The role that the message plays in the message.
    Valid Values: user | assistant.
    """
    USER = 'user'
    ASSISTANT = 'assistant'


@dataclass
class InferenceConfig:
    """
    Base inference parameters to pass to a model in a call to Converse. 
    For more information, see Inference parameters for foundation models.
    """
    max_tokens: int = 500
    stop_sequences: List[str] = None
    temperature: float = 0.5
    top_p: float = 0.5
    top_k: int = None

    def __post_init__(self):
        if self.stop_sequences is None:
            self.stop_sequences = []
        return
    
    def _to_dict(self):
        return {
            'maxTokens': self.max_tokens,
            'temperature': self.temperature,
            'topP': self.top_p,
            'stopSequences': self.stop_sequences
        }

@dataclass
class ContentText:
    """
    Text content for a message.

    :param text (str): The text to add to the message.
    """
    text: str

    def _to_dict(self):
        return {
            'text': self.text
        }


@dataclass
class Message:
    """
    A message in the Message field. Use to send a message in a call to Converse. 
    
    :param content (list): Type: Array of ContentBlock objects
    :param role (Roles): The role that the message plays in the message.
    """

    content: List[Union[ContentText, ContentVision, ContentToolResults]] = None
    role: Roles = Roles.USER

    def __post_init__(self):
        if self.content is None:
            self.content = []
        return
    
    def _to_dict(self):
        return {
            'role': self.role,
            'content': [content_block._to_dict() for content_block in self.content]
        }

@dataclass
class Conversation:
    """
    A conversation with a Bedrock Foundation Model.

    :param bedrock_runtime_client (boto3.client): boto3 client to make converse API requests.
    :param model (FoundationModels): The bedrock foundation model to use for the conversation.
    :param config (InferenceConfiguration): The inference configuration to use for the conversation.
    :param system (str): A system prompt to pass to the model.
    :param messages (ist[Message]): A single message or message history to send to the model.
        For models that do not support a list of messages, the list of messages is concatinated into a single message.
    :param history (bool): when true, converse API responses are added to the messages automatically
        when false, messages is defaulted to [] after each call to converse.
    :param tool_state (ToolState): Used to determine if a tool is in use, and if so what step it is in.
    :param debug (bool): display converse API request and response data.
    """
    bedrock_runtime_client: any = None
    model: Models = Models.AMAZON_TITAN_PREMIER
    config: InferenceConfig = None
    system: str = None
    messages: list[Message] = None
    history: bool = True
    tools: List[Tool] = None
    _tool_state: ToolState = ToolState.NONE
    _tool_use_id: str = None
    _tool_name: str = None
    _tool_inputs: Dict = None
    debug: bool = False

    @property
    def tool_state(self):
        return self._tool_state
    
    @property
    def tool_use_id(self):
        return self._tool_use_id

    @property
    def tool_name(self):
        return self._tool_name

    @property
    def tool_inputs(self):
        return self._tool_inputs


    def __post_init__(self):
        if self.bedrock_runtime_client is None:
            self.bedrock_runtime_client = boto3.client('bedrock-runtime')
        if self.config is None:
            self.config = InferenceConfig()
        if self.messages is None:
            self.messages = []
        if self.tools is None:
            self.tools = []
        return


    def converse(self):
        """
        Sends messages to the specified Amazon Bedrock model.
        Wrapper for the boto3 bedrock-runtime converse API.
        """
        request = self.request_parameters()
        if self.debug:
            self._print_request(request)
        response = self.bedrock_runtime_client.converse(**request)
        #assistant_text = response['output']['message']['content'][0]['text']
        assistant_message = response['output']['message']['content']
        if self.debug:
            print(json.dumps(response, indent=4))
        if self.history:
            self._add_assistant_response_to_messages(assistant_message)
        else:
            self.messages = []
        if self._tool_state == ToolState.SELECT:
            self._set_tool_use_config(response)
            self._tool_state == ToolState.RUNNING
        elif self._tool_state == ToolState.RESULTS:
            self._reset_tool_use_config()
        if 'text' in assistant_message[0]:
            assistant_text = assistant_message[0]['text']
        else:
            assistant_text = ''
        return assistant_text


    def request_parameters(self) -> dict:
        """
        Returns the message as a dictionary in the format expected by the converse API.
        """
        parameters = {}
        parameters['modelId'] = self.model
        parameters['inferenceConfig'] = self._inference_config_to_dict()
        if self.system is not None:
            system = self._system_to_dict()
            if system is not None:
                parameters['system'] = system
        parameters['messages'] = self._messages_to_dict()
        if len(self.tools) > 0:
            parameters['toolConfig'] = {}
            parameters['toolConfig']['tools'] = self._tools_to_dict()
            if self._tool_state == ToolState.NONE:
                self._tool_state = ToolState.SELECT
            elif self.tool_state == ToolState.RUNNING:
                self._tool_state = ToolState.RESULTS

        return parameters


    def _inference_config_to_dict(self):
        return self.config._to_dict()


    def _system_to_dict(self):
        """
        A system prompt to pass to the model in the format for Converse API.
        If the model does not support the system prompt then the system
        prompt is inserted into the messages.
        """
        if self.model.metadata.system_message_support:
            return [{'text': self.system}]
        else:
            self._system_to_messages_for_unsupported_models()
        return None


    def _system_to_messages_for_unsupported_models(self):
        message = Message(role=Roles.USER)
        message.content.append(ContentText(self.system))
        self.messages.insert(0, message)

        message = Message(role=Roles.ASSISTANT)
        message.content.append(ContentText('OK.'))
        self.messages.insert(1, message)

        return None
     

    def _messages_to_dict(self):
        """
        Returns a list of messages in the format expected by the converse API.
        """
        if self.model.metadata.message_history_support:
            return [message._to_dict() for message in self.messages]
        else:
            return self._message_to_dict_for_unsupported_models()


    def _message_to_dict_for_unsupported_models(self):
        """
        AI21 J2 models do not support chat history.
        "This model doesn't support conversation history."
        To work around each message text is first prefixed with a role, then
        all message text is concatenated into a single string. 
        A single message is then returned.
        """
        text = ''
        if self.model.startswith('ai21.j2'):
            user_role = 'Human:'
            assistant_role = 'AI:'
        for message in self.messages:
            if message.role == Roles.USER:
                text += f'{user_role} {message.content[0].text}\n'
            elif message.role == Roles.ASSISTANT:
                text += f'{assistant_role} {message.content[0].text}\n'
        text += f'{assistant_role}'
        return [{
            'role': Roles.USER,
            'content': [{'text': text}]
        }] 


    def _tools_to_dict(self):
        return [tool._to_dict() for tool in self.tools]


    def _set_tool_use_config(self, response) -> str:
        for content in response['output']['message']['content']:
            if 'toolUse' in content:
                self._tool_use_id = content['toolUse']['toolUseId']
                self._tool_name = content['toolUse']['name']
                self._tool_inputs = content['toolUse']['input']
                break
        return


    def _reset_tool_use_config(self):
        self._tool_state == ToolState.NONE
        self._tool_use_id = None
        self._tool_name = None
        self._tool_inputs = None
        return
    

    def _add_assistant_response_to_messages(self, assistant_message):
        """
        Add the last assistant text from converse response to messages.
        Results in messages being the chat history.
        """
        message = Message(role=Roles.ASSISTANT)
        for assistant_content in assistant_message:
            if 'text' in assistant_content:
                message.content.append(ContentText(**assistant_content))
            elif 'toolUse' in assistant_content:
                tool_use = {
                    'tool_use_id': assistant_content['toolUse']['toolUseId'],
                    'name': assistant_content['toolUse']['name'],
                    'input': assistant_content['toolUse']['input']
                }
                message.content.append(ContentToolUse(**tool_use))
        self.messages.append(message)
        return


    def _print_request(self, request):
        """
        Pretty prints the converse API request, filtering out image bytes when present.
        """
        request_copy = copy.deepcopy(request)
        for message in request_copy['messages']:
            for content_block in message['content']:
                if 'image' in content_block:
                    content_block['image']['source']['bytes'] = 'IMAGE_BYTES_NOT_SHOWN'
        print(json.dumps(request_copy, indent=4))
