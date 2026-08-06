import { useEffect, useState, useTransition } from "react";
import {
  Button,
  Group,
  TextInput,
  Title,
  Stack,
  Box,
  Paper,
  Loader,
  Center,
} from "@mantine/core";
import { SongsTable } from "@/components/SongsTable";
import { SongsGrid } from "@/components/SongsGrid";
import { useLibrary } from "@/contexts/LibraryContext";
import {
  ViewMode,
  ViewToggleButton,
} from "@/components/input/ViewToggleButton";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { songsQuery } from "@/api";

export function Component() {
  const { setSongs } = useLibrary();
  const [_isPending, startTransition] = useTransition();
  const [mode, setMode] = useState<ViewMode>(ViewMode.CARD);
  const [activePath, setActivePath] = useState(
    "/Users/school/Music/twenty one pilots",
  );
  const queryClient = useQueryClient();
  const [inputPath, setInputPath] = useState("");

  const { data: songs, isFetching } = useQuery(songsQuery(activePath));

  useEffect(() => {
    if (songs) setSongs(songs);
  }, [setSongs, songs]);

  return (
    <Stack pos="relative" h="100%">
      <Paper p="md" pos="sticky" top={0}>
        <Stack gap="sm">
          <Group>
            <Title order={2} mr="auto">
              Search Directory
            </Title>
            <Button
              variant="subtle"
              onClick={() =>
                queryClient.invalidateQueries({
                  queryKey: ["songs", activePath],
                })
              }
            >
              Refresh
            </Button>
            <ViewToggleButton
              onChange={(mode) => startTransition(() => setMode(mode))}
              value={mode}
            />
          </Group>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (!inputPath.trim()) return;
              setActivePath(inputPath);
            }}
          >
            <Group gap="xs">
              <TextInput
                id="scan-input"
                value={inputPath}
                onChange={(e) => setInputPath(e.currentTarget.value)}
                placeholder="Enter a path..."
                flex={1}
              />
              <Button type="submit" loading={isFetching}>
                Scan
              </Button>
            </Group>
          </form>
        </Stack>
      </Paper>
      <Box flex={1} mih={0} p="md" style={{ overflow: "auto" }}>
        {isFetching ? (
          <Center h="100%">
            <Loader />
          </Center>
        ) : mode === ViewMode.CARD ? (
          <SongsGrid />
        ) : (
          <SongsTable />
        )}
      </Box>
    </Stack>
  );
}
