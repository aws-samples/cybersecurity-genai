import LoadingBar from "@cloudscape-design/chat-components/loading-bar";
import Box from "@cloudscape-design/components/box";


interface AiLoadingBarProps {
  rationaleText: string;
}


export default function AiLoadingBar (props: AiLoadingBarProps) {
  return (
    <div aria-live="polite">
      <Box
        margin={{ bottom: "xs", left: "l" }}
        color="text-body-secondary"
      >
        {props.rationaleText}
      </Box>
      <LoadingBar variant="gen-ai" />
    </div>
  );
}
