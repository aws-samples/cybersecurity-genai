// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0



import { Amplify } from 'aws-amplify';



Amplify.configure({
    Auth: {
      Cognito: {
          userPoolId: import.meta.env.VITE_UserPoolId,
          userPoolClientId: import.meta.env.VITE_UserPoolClientId,
          identityPoolId: import.meta.env.VITE_IdentityPoolId,
          loginWith: {
              email: true,
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
