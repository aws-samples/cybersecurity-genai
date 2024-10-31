// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0



import { Link, LinkProps } from "@cloudscape-design/components";
import { useOnFollow } from "../../common/hooks/use-on-follow";

export default function RouterLink(props: LinkProps) {
  const onFollow = useOnFollow();

  return <Link {...props} onFollow={onFollow} />;
}
