// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0



import {
  ButtonDropdownProps,
  ButtonDropdown,
} from "@cloudscape-design/components";
import { useOnFollow } from "../../common/hooks/use-on-follow";

export default function RouterButtonDropdown(props: ButtonDropdownProps) {
  const onFollow = useOnFollow();

  return <ButtonDropdown {...props} onItemFollow={onFollow} />;
}
