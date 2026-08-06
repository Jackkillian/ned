import { useEffect, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import {
  Button,
  Group,
  TextInput,
  Title,
  Stack,
  Box,
  LoadingOverlay,
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
  const [mode, setMode] = useState<ViewMode>(ViewMode.CARD);
  const [loading, setLoading] = useState(false);
  const [path, setPath] = useState("");
  const { setSongs } = useLibrary();

  useEffect(() => {
    loadSongs("/Users/school/Music/twenty one pilots/").then((songs) =>
      setSongs(songs),
    );
  }, [setSongs]);

  return (
    <Stack pos="relative" h="100%">
      <LoadingOverlay
        visible={loading}
        zIndex={1000}
        overlayProps={{ radius: "sm", blur: 2 }}
      />
      <Paper p="md" pos="sticky" top={0}>
        <Stack gap="sm">
          <Group>
            <Title order={2} mr="auto">
              Search Directory
            </Title>
            <ViewToggleButton onChange={setMode} value={mode} />
          </Group>
          <form
            onSubmit={async (e) => {
              e.preventDefault();
              setLoading(true);
              setSongs(await loadSongs(path));
              setLoading(false);
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
              <Button type="submit">Scan</Button>
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
