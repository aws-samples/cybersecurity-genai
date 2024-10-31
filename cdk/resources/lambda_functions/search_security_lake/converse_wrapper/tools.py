# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Union, Dict, List


class ToolState(StrEnum):
    """
    Used to track the state of the tool. The tool has 4 steps when it runs
    which have been turned into 4 states:
    - TOOL_SELECT: Step 1: Send the message and tool definition
    - TOOL_USE: Step 2: Get the tool request from the model
    - TOOL_RESULTS: Step 3: Make the tool request for the model
    - TOOL_RESPONSE: Step 4: Get the model response
    The None state means a tool is not in process.
    - NONE: No tool in use at this time.

    Read more about bedrock converse api tools here
    https://docs.aws.amazon.com/bedrock/latest/userguide/tool-use.html
    """
    NONE = 'no_tool'
    SELECT = 'begin'
    RUNNING = 'tool_use'
    RESULTS = 'tool_results'
    RESPONSE = 'end'

class ToolPropertyTypes(StrEnum):
    STRING = 'string'
    NUMBER = 'number'
    INTEGER = 'integer'
    OBJECT = 'object'
    ARRAY = 'array'
    BOOLEAN = 'boolean'

@dataclass
class ContentToolUse:
    """
    Information about a tool use request from a model.
    """
    tool_use_id: str
    name: str
    input: dict

    def _to_dict(self):
        return {
            'toolUse': {
                'toolUseId': self.tool_use_id,
                'name': self.name,
                'input': self.input
            }
        }

@dataclass
class ContentToolResults:
    """
    A tool result block that contains the results for a tool request that the model previously made.
    """
    tool_use_id: str
    results: Union[Dict, str]

    def _to_dict(self):
        if type(self.results) is str:
            content = {'text': self.results}
        elif type(self.results) is dict:
            content = {
                'json': self.results
            }
        return {
            'toolResult': {
                'toolUseId': self.tool_use_id,
                'content': [
                    content
                ]
            }
        }

@dataclass
class ToolProperty:
    name: str
    description: str
    type: ToolPropertyTypes = ToolPropertyTypes.STRING
    enum: List = None
    required: bool = True

    def __post_init__(self):
        if self.enum is None:
            self.enum = None
        return

    def _to_dict(self):
        tool_property = {}
        tool_property['type'] = self.type
        tool_property['description'] = self.description
        if self.enum is not None:
            tool_property['enum'] = self.enum

        return tool_property

@dataclass
class Tool:
    name: str
    description: str
    properties: List[ToolProperty] = field(default_factory=list)

    def _to_dict(self):
        tool_spec = {}
        tool_spec['toolSpec'] = {}
        tool_spec['toolSpec']['name'] = self.name
        tool_spec['toolSpec']['description'] = self.description
        tool_spec['toolSpec']['inputSchema'] = {}
        tool_spec['toolSpec']['inputSchema']['json'] = {}
        tool_spec['toolSpec']['inputSchema']['json']['type'] = 'object'
        properties = {}
        required_properties = []
        for prop in self.properties:
            properties[prop.name] = prop._to_dict()
            if prop.required:
                required_properties.append(prop.name)
        tool_spec['toolSpec']['inputSchema']['json']['properties'] = properties
        if required_properties:
            tool_spec['toolSpec']['inputSchema']['json']['required'] = required_properties
        return tool_spec
