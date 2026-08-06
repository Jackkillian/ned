import {
  ActionIcon,
  Burger,
  Group,
  Text,
  useMantineColorScheme,
  useComputedColorScheme,
} from "@mantine/core";
import { MinusIcon, XIcon, SunIcon, MoonIcon } from "@phosphor-icons/react";
import { useRef } from "react";
import { getCurrentWindow } from "@tauri-apps/api/window";
import classes from "./TitleBar.module.css";

function TemporaryColorSchemeButton() {
  const { setColorScheme } = useMantineColorScheme();
  const computedColorScheme = useComputedColorScheme("light", {
    getInitialValueInEffect: true,
  });

  return (
    <ActionIcon
      onClick={() =>
        setColorScheme(computedColorScheme === "light" ? "dark" : "light")
      }
      size="md"
    >
      {computedColorScheme === "light" ? (
        <SunIcon size={24} />
      ) : (
        <MoonIcon size={24} />
      )}
    </ActionIcon>
  );
}

export function TitleBar({
  opened,
  toggle,
}: {
  opened: boolean;
  toggle: () => void;
}) {
  const appWindowRef = useRef(getCurrentWindow());

  return (
    <Group
      gap={8}
      p="xs"
      h="100%"
      wrap="nowrap"
      c="white"
      bg="blue"
      style={{ userSelect: "none", WebkitUserSelect: "none" }}
      className={classes.titlebar}
      data-tauri-drag-region
    >
      <Burger
        opened={opened}
        onClick={toggle}
        color="white"
        bdrs="md"
        size="sm"
      />
      <Text data-tauri-drag-region mr="auto">
        Ned
      </Text>
      <ActionIcon onClick={() => appWindowRef.current.minimize()}>
        <MinusIcon size={24} color="white" />
      </ActionIcon>
      <ActionIcon onClick={() => appWindowRef.current.close()}>
        <XIcon size={24} color="white" />
      </ActionIcon>
      <TemporaryColorSchemeButton />
    </Group>
  );
}
