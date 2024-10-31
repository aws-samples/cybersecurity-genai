// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0


import {
  Box,
  Button,
  Container,
  Popover,
  StatusIndicator,
} from "@cloudscape-design/components";
import { ChatMessage } from "../ChatUI/types";
import remarkGfm from "remark-gfm";
import ReactMarkdown from "react-markdown";
import styles from "../../styles/chat-ui.module.scss";
import AiAvatar from "../AiAvatar";
import AiLoadingBar from "../LoadingBar";



interface AiChatMessageProps {
    message: ChatMessage;
    rationaleText: string;
    showCopyButton?: boolean;
}

export default function AiChatContainer(aiProps: AiChatMessageProps) {
  return (
    <Container>
        <AiAvatar />
        {aiProps.message.content.length === 0 ? (
          <Box>
            <AiLoadingBar rationaleText={aiProps.rationaleText}/>
          </Box>
        ) : null}
        {aiProps.message.content.length > 0 && aiProps.showCopyButton !== false ? (
          <div className={styles.btn_chabot_message_copy}>
            <Popover
              size="medium"
              position="top"
              triggerType="custom"
              dismissButton={false}
              content={
                <StatusIndicator type="success">
                  Copied to clipboard
                </StatusIndicator>
              }
            >
              <Button
                variant="inline-icon"
                iconName="copy"
                onClick={() => {
                  navigator.clipboard.writeText(aiProps.message.content);
                }}
              />
            </Popover>
          </div>
        ) : null}
        <ReactMarkdown
          children={aiProps.message.content}
          remarkPlugins={[remarkGfm]}
          components={{
            pre(props) {
              const { children, ...rest } = props;
              return (
                <pre {...rest} className={styles.codeMarkdown}>
                  {children}
                </pre>
              );
            },
            table(props) {
              const { children, ...rest } = props;
              return (
                <table {...rest} className={styles.markdownTable}>
                  {children}
                </table>
              );
            },
            th(props) {
              const { children, ...rest } = props;
              return (
                <th {...rest} className={styles.markdownTableCell}>
                  {children}
                </th>
              );
            },
            td(props) {
              const { children, ...rest } = props;
              return (
                <td {...rest} className={styles.markdownTableCell}>
                  {children}
                </td>
              );
            },
          }}
        />
      </Container>
    );
  }
 