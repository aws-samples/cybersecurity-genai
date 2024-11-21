# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import aws_cdk
from stacks.frontend.stack import FrontEnd
from stacks.frontend.constants import FrontEndProps

from stacks.embedding_processor.stack import EmbeddingProcessor
from stacks.embedding_processor.constants import EmbeddingProcessorProps

from stacks.awsdocs.stack import AwsDocs
from stacks.awsdocs.constants import AwsDocsProps

from stacks.agent.stack import Agent
from stacks.agent.constants import AgentProps

from stacks.observability.stack import Observability
from stacks.observability.constants import ObservabilityProps

from config import EMAIL



if not EMAIL or not EMAIL.strip():
    exit("Please provide a valid email address in cdk/config.py")



app = aws_cdk.App()

frontend = FrontEnd(
    app, 
    FrontEndProps.STACK_NAME, 
    description=FrontEndProps.STACK_DESCRIPTION
)

embedding_processor = EmbeddingProcessor(
    app, 
    EmbeddingProcessorProps.STACK_NAME, 
    description=EmbeddingProcessorProps.STACK_DESCRIPTION
)

knowledge_base = AwsDocs(
    app, 
    AwsDocsProps.STACK_NAME, 
    description=AwsDocsProps.STACK_DESCRIPTION
)

agent = Agent(
    app, 
    AgentProps.STACK_NAME, 
    description=AgentProps.STACK_DESCRIPTION, 
    aoss_collection=embedding_processor.collection,
    bedrock_kb=knowledge_base.kb
)

observability = Observability(
    app, 
    ObservabilityProps.STACK_NAME, 
    description=ObservabilityProps.STACK_DESCRIPTION
)

app.synth()
