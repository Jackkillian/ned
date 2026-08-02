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
} from "@mantine/core";
import { SongsTable } from "../components/SongsTable";
import { SongsGrid } from "@/components/SongsGrid";
import { useLibrary } from "@/contexts/LibraryContext";
import { Song } from "@/types/Song";

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
      <Box
        p="md"
        bg="white"
        pos="sticky"
        top={0}
        style={{
          zIndex: 10,
          borderBottom: "1px solid var(--mantine-color-gray-2)",
        }}
      >
        <Stack gap="sm">
          <Title order={2}>Search Directory</Title>
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
      </Box>
      <Box flex={1} mih={0} p="md" style={{ overflow: "auto" }}>
        <SongsGrid />
        <SongsTable />
      </Box>
    </Stack>
  );
}
