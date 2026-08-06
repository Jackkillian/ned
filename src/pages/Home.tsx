import { useEffect, useState, useTransition } from "react";
import { invoke } from "@tauri-apps/api/core";
import {
  Button,
  Group,
  TextInput,
  Title,
  Stack,
  Box,
  Paper,
} from "@mantine/core";
import { SongsTable } from "../components/SongsTable";
import { SongsGrid } from "@/components/SongsGrid";
import { useLibrary } from "@/contexts/LibraryContext";
import { Song } from "@/types/Song";
import {
  ViewMode,
  ViewToggleButton,
} from "@/components/input/ViewToggleButton";

/**
 * @param path - Directory path to scan
 * @returns A list of songs in the given directory
 */
async function loadSongs(path: string): Promise<Song[]> {
  try {
    return await invoke("scan", { path });
  } catch (error) {
    console.error("Failed to scan directory:", error);
    return [];
  }
}

export function Component() {
  const [isPending, startTransition] = useTransition();
  const [mode, setMode] = useState<ViewMode>(ViewMode.CARD);
  const [path, setPath] = useState("");
  const { setSongs } = useLibrary();

  useEffect(() => {
    startTransition(async () => {
      const songs = await loadSongs("/Users/school/Music/twenty one pilots/");
      startTransition(() => setSongs(songs));
    });
  }, [setSongs]);

  return (
    <Stack pos="relative" h="100%">
      <Paper p="md" pos="sticky" top={0}>
        <Stack gap="sm">
          <Group>
            <Title order={2} mr="auto">
              Search Directory
            </Title>
            <ViewToggleButton
              onChange={(mode) => startTransition(() => setMode(mode))}
              value={mode}
            />
          </Group>
          <form
            onSubmit={async (e) => {
              e.preventDefault();
              startTransition(async () => {
                const songs = await loadSongs(path);
                startTransition(() => setSongs(songs));
              });
            }}
          >
            <Group gap="xs">
              <TextInput
                id="scan-input"
                value={path}
                onChange={(e) => setPath(e.currentTarget.value)}
                placeholder="Enter a path..."
                flex={1}
              />
              <Button type="submit" loading={isPending}>
                Scan
              </Button>
            </Group>
          </form>
        </Stack>
      </Paper>
      <Box flex={1} mih={0} p="md" style={{ overflow: "auto" }}>
        {mode === ViewMode.CARD ? <SongsGrid /> : <SongsTable />}
      </Box>
    </Stack>
  );
}
