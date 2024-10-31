name = 'search-security-lake'
description = 'Search VPC Flowlogs, Route53 Logs, CloudTrail Management Events, S3 Data Events, Lambda Data Events and Security Hub Findings.'
schema = """openapi: 3.0.0
info:
  title: search-security-lake
  version: 1.0.0
  description: Search AWS VPC Flowlogs, Amazon Route53 Logs, AWS CloudTrail Management Events, Amazon S3 Data Events, AWS Lambda Data Events and AWS Security Hub Findings.

paths:
  /search-vpc-flow-logs:
    post:
      summary: Search AWS VPC Flow Logs.
      description: Search VPC Flow Logs by IP address, port number, or network interface ID (ENI ID). For example, this endpoint can be used to find logs related to SSH traffic (destination port 22, TCP protocol) from a specific IP address to a specific network interface.
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

  /search-route-53:
    post:
      summary: Search for DNS queries in Amazon Route 53
      description: Search Route 53 logs for DNS queries by record type, hostname, source IP, and time range. Returns query details like hostname, type, source IP, timestamp, response data, and response code.
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
          
  /search-cloudtrail:
    post:
      summary: Search AWS CloudTrail Management Events
      description: Search AWS CloudTrail logs for management events related to API calls across various AWS services. Filter events by service name, API action, source IP address, IAM identity, and time range. Returns details about matching events, including the service, action, caller identity, source IP, and event timestamp.
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
          
  /search-lambda-invoke-events:
    post:
      summary: Search AWS Lambda Invoke Events
      description: Search AWS Lambda function execution, invocation activity (the Invoke API).
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
          
  /search-s3-data-events:
    post:
      summary: Search Amazon S3 Data Events
      description: Search S3 Data Events for example Get object, Delete Object and Put Object events.
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
          
  /search-security-hub:
    post:
      summary: Search AWS Security Hub for findings.
      description: Searches and retrieves security findings. Findings are for AWS Resources from AWS Services include GuardDuty, Inspector, Config, Audit Manager, Detective, Firewall Manager, Health, IAM Access Analyzer, Macie and Trusted Advisor. Findings are rated by severity INFORMATIONAL, LOW, MEDIUM, HIGH or CRITICAL.
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
        - user_input
      properties:
        user_input:
          type: string
          description: Proxy the users input.

  responses:
    SuccessfulResponse:
      description: Successful response
      content:
        text/plain:
          schema:
            type: string
            example: 'The query results as a string.'

    BadRequest:
      description: Bad request
      content:
        text/plain:
          schema:
            type: string
            example: 'Invalid request parameters.'

    InternalServerError:
      description: Internal server error
      content:
        text/plain:
          schema:
            type: string
            example: 'An error occurred while processing the request.'
"""
