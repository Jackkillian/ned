import { ActionIcon } from "@mantine/core";
import { GridFourIcon, TableIcon } from "@phosphor-icons/react";

export enum ViewMode {
  CARD,
  TABLE,
}

export function ViewToggleButton({
  onChange,
  value,
}: {
  onChange: (value: ViewMode) => void;
  value: ViewMode;
}) {
  return (
    <ActionIcon
      onClick={() =>
        onChange(value === ViewMode.CARD ? ViewMode.TABLE : ViewMode.CARD)
      }
      size="lg"
      variant="subtle"
    >
      {value === ViewMode.CARD ? (
        <GridFourIcon size={24} />
      ) : (
        <TableIcon size={24} />
      )}
    </ActionIcon>
  );
}
