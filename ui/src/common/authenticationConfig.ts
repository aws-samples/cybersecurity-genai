// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0



import { Amplify } from 'aws-amplify';
import config from './cdkOutput.json'



Amplify.configure({
    Auth: {
      Cognito: {
          userPoolId: config.CybersecurityGenAIDemo.COGNITOUSERPOOLID,
          userPoolClientId: config.CybersecurityGenAIDemo.COGNITOUSERPOOLCLIENTID,
          identityPoolId: config.CybersecurityGenAIDemo.COGNITOIDENTITYPOOLID,
          loginWith: {
              email: true,
          },
          signUpVerificationMethod: 'code',
          userAttributes: {
              email: {
                  required: true
              }
          },
          passwordFormat: {
              minLength: 8,
              requireLowercase: true,
              requireUppercase: true,
              requireNumbers: true,
              requireSpecialCharacters: true,
          },
  
      },
    }
})

export const authConfig=Amplify.getConfig()
