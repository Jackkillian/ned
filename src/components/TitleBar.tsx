import {
  ActionIcon,
  Burger,
  Group,
  Text,
  useMantineColorScheme,
  useComputedColorScheme,
} from "@mantine/core";
import classes from "./TitleBar.module.css";
import { MinusIcon, XIcon, SunIcon, MoonIcon } from "@phosphor-icons/react";
import { useRef } from "react";
import { getCurrentWindow } from "@tauri-apps/api/window";

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
      variant="default"
      size="md"
    >
      {computedColorScheme === "light" ? <SunIcon /> : <MoonIcon />}
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
      p="sm"
      h="100%"
      wrap="nowrap"
      className={classes.titlebar}
      data-tauri-drag-region
    >
      <Burger opened={opened} onClick={toggle} color="white" />
      <TemporaryColorSchemeButton />
      <Text data-tauri-drag-region mr="auto">
        Ned
      </Text>
      <ActionIcon onClick={() => appWindowRef.current.minimize()}>
        <MinusIcon size={24} color="white" />
      </ActionIcon>
      <ActionIcon onClick={() => appWindowRef.current.close()}>
        <XIcon size={24} color="white" />
      </ActionIcon>
    </Group>
  );
}
