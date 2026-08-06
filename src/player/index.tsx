import "@mantine/core/styles.css";
import React, { useEffect, useRef, useState } from "react";
import ReactDOM from "react-dom/client";
import {
  Group,
  Text,
  Image,
  Paper,
  MantineProvider,
  Stack,
  Center,
} from "@mantine/core";
import { getCurrentWindow } from "@tauri-apps/api/window";
import { getCurrentWebviewWindow } from "@tauri-apps/api/webviewWindow";
import { Audio } from "@gfazioli/mantine-audio";
import { convertFileSrc } from "@tauri-apps/api/core";
import { Song } from "@/types/Song";

// document.oncontextmenu = document.body.oncontextmenu = () => false;

function Player() {
  const appWindowRef = useRef(getCurrentWindow());
  const [currentSong, setCurrentSong] = useState<Song | null>(null);

  useEffect(() => {
    const appWebview = getCurrentWebviewWindow();
    const unlisten = appWebview.listen("start", (event) => {
      const song = JSON.parse(event.payload as string) as Song;
      console.log("GOT SONG", song);
      setCurrentSong(song);
    });

    return () => {
      unlisten.then((fn) => fn());
    };
  }, []);

  if (!currentSong)
    return (
      <Paper
        w="100vw"
        h="100vh"
        onMouseDown={() => appWindowRef.current.startDragging()}
      >
        <Center h="100vh">
          <Text c="dimmed">No active song</Text>
        </Center>
      </Paper>
    );

  return (
    <Paper
      w="100%"
      h="100vh"
      p="sm"
      onMouseDown={() => appWindowRef.current.startDragging()}
    >
      <Group align="center" gap="md" wrap="nowrap" w="100%" h="100%">
        {currentSong.tag_data?.picture && (
          <Image
            w="90vh"
            h="90vh"
            radius="md"
            src={currentSong.tag_data.picture}
            alt="Album Cover"
            draggable="false"
          />
        )}
        <Stack flex={1} miw={0} style={{ overflow: "hidden" }}>
          <Audio
            key={currentSong.path}
            src={convertFileSrc(currentSong.path)}
            controls={false}
            flex={1}
            autoPlay
          >
            <Audio.Waveform height={24} />
            <Group justify="space-between" wrap="nowrap" mt="sm">
              <Group gap="xs">
                <Audio.SkipButton seconds={-10} />
                <Audio.PlayButton />
                <Audio.SkipButton seconds={10} />
              </Group>
              <Audio.TimeDisplay />
              <Audio.MuteButton />
            </Group>
          </Audio>
          <Group gap="sm">
            <Text flex={1} fz="sm" truncate="end">
              {currentSong.tag_data?.title}
            </Text>
            <Text fz="sm" c="dimmed">
              {currentSong.tag_data?.artist}
            </Text>
          </Group>
        </Stack>
      </Group>
    </Paper>
  );
}

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <MantineProvider>
      <Player />
    </MantineProvider>
  </React.StrictMode>,
);
