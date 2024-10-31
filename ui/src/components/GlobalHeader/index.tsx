// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0



import { useState } from "react";
import { Amplify } from 'aws-amplify';
import { signOut } from 'aws-amplify/auth';
import { authConfig } from "../../common/authenticationConfig";
import { TopNavigation } from "@cloudscape-design/components";
import { Mode } from "@cloudscape-design/global-styles";
import { StorageHelper } from "../../common/helpers/storage-helper";
import { APP_NAME } from "../../common/constants";



Amplify.configure(authConfig);
async function handleSignOut() {
  await signOut()
}

export default function GlobalHeader() {
  const [theme, setTheme] = useState<Mode>(StorageHelper.getTheme());

  const onChangeThemeClick = () => {
    if (theme === Mode.Dark) {
      setTheme(StorageHelper.applyTheme(Mode.Light));
    } else {
      setTheme(StorageHelper.applyTheme(Mode.Dark));
    }
  };

  return (
    <div
      style={{ zIndex: 1002, top: 0, left: 0, right: 0, position: "fixed" }}
      id="awsui-top-navigation"
    >
      <TopNavigation
        identity={{
          href: "/",
          title: "AWS Cybersecurity GenAI Demo"
        }}
        utilities={[
          {
            type: "button",
            text: "AWS Cloud Security",
            href: "https://aws.amazon.com/security/",
            external: true,
            externalIconAriaLabel: " (opens in a new tab)"
          },  
          {
            type: "button",
            text: theme === Mode.Dark ? "Light Mode" : "Dark Mode",
            onClick: onChangeThemeClick,
          },
          {
            type: "button",
            text: "Sign Out",
            onClick: handleSignOut
          }
        ]}
      />
    </div>
  );
}
