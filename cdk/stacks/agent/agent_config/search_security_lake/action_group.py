name = 'search-security-lake'
description = 'Search security logs and events from multiple AWS and third-party sources for cybersecurity analysis and incident response.'
schema = """openapi: 3.0.0
info:
  title: search-security-lake
  version: 1.0.0
  description: Search security logs and events from multiple AWS and third-party sources for cybersecurity analysis and incident response.

paths:
  /cloudtrail-mgmt:
    get:
      summary: AWS CloudTrail management events
      description: Search AWS CloudTrail logs for management events, including user activity and API calls across AWS services.
      operationId: cloudtrail-mgmt
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/QueryRequest'
      responses:
        '200':
          $ref: '#/components/responses/SuccessfulResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '500':
          $ref: '#/components/responses/InternalServerError'

  /s3-data-events:
    get:
      summary: CloudTrail data events for S3
      description: Search CloudTrail logs for S3 data events, including object-level operations like GetObject and PutObject.
      operationId: s3-data-events
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/QueryRequest'
      responses:
        '200':
          $ref: '#/components/responses/SuccessfulResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '500':
          $ref: '#/components/responses/InternalServerError'

  /lambda-data-events:
    get:
      summary: CloudTrail data events for Lambda
      description: Search CloudTrail logs for Lambda function invocations and related activities.
      operationId: lambda-data-events
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/QueryRequest'
      responses:
        '200':
          $ref: '#/components/responses/SuccessfulResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '500':
          $ref: '#/components/responses/InternalServerError'

  /security-hub:
    get:
      summary: AWS Security Hub findings
      description: Retrieve and analyze security findings from AWS Security Hub, including compliance checks and security best practices.
      operationId: security-hub
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/QueryRequest'
      responses:
        '200':
          $ref: '#/components/responses/SuccessfulResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '500':
          $ref: '#/components/responses/InternalServerError'

  /route53-logs:
    get:
      summary: Amazon Route 53 resolver query logs
      description: Search and analyze DNS query logs from Amazon Route 53 for potential security issues or suspicious activities.
      operationId: route53-logs
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/QueryRequest'
      responses:
        '200':
          $ref: '#/components/responses/SuccessfulResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '500':
          $ref: '#/components/responses/InternalServerError'

  /vpc-flow-logs:
    get:
      summary: Amazon Virtual Private Cloud (Amazon VPC) Flow Logs
      description: Analyze VPC Flow Logs for network traffic patterns, potential security threats, and troubleshooting network issues.
      operationId: vpc-flow-logs
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/QueryRequest'
      responses:
        '200':
          $ref: '#/components/responses/SuccessfulResponse'
        '400':
          $ref: '#/components/responses/BadRequest'
        '500':
          $ref: '#/components/responses/InternalServerError'

components:
  schemas:
    QueryRequest:
      type: object
      required:
        - user-input
        - similarity-search
      properties:
        user-input:
          type: string
          description: The user's query in natural language, describing the security information they're looking for.
        similarity-search:
          type: boolean
          description: Set to false for queries with explicit terms, timestamps, or known event types. Enable (set to true) only when the query is broad, conceptual, or doesn't contain specific identifiers.
    
  responses:
    SuccessfulResponse:
      description: Successful response
      content:
        text/plain:
          schema:
            type: string

    BadRequest:
      description: Bad request
      content:
        text/plain:
          schema:
            type: string

    InternalServerError:
      description: Internal server error
      content:
        text/plain:
          schema:
            type: string
"""
