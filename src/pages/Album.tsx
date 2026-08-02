import { AlbumArt } from "@/components/AlbumArt";
import { useLibrary } from "@/contexts/LibraryContext";
import { getFileName } from "@/utils";
import { Anchor, Group, Stack, Text, Title } from "@mantine/core";
import { emitTo } from "@tauri-apps/api/event";
import { DataTable } from "mantine-datatable";
import { useMemo } from "react";
import { useParams } from "react-router";

export function Component() {
  const { album } = useParams() as { album: string };
  const library = useLibrary();
  const songs = useMemo(
    () => library.getSongsByAlbum()[album] ?? [],
    [library, album],
  );
  const albumArt = songs[0]?.tag_data?.picture;

  return (
    <Stack mt="md">
      <Group>
        <AlbumArt albumArt={albumArt} size={128} />
        <Stack gap="sm">
          <Group align="baseline">
            <Title>{album}</Title>
            <Text c="dimmed">
              {songs[0]?.tag_data?.artist ?? "<no artist>"} •{" "}
              {songs[0]?.tag_data?.year ?? "<no year>"}
            </Text>
          </Group>
        </Stack>
      </Group>
      <DataTable
        columns={[
          {
            accessor: "title",
            render: (row) => (
              <Anchor
                onClick={() =>
                  emitTo("player", "start", JSON.stringify(row.song))
                }
              >
                <Text truncate="end" maw="400px" fz="sm">
                  {row.title ?? getFileName(row.song.path)}
                </Text>
              </Anchor>
            ),
          },
          { accessor: "disc_number" },
          { accessor: "track_number" },
        ]}
        records={songs
          .sort((a, b) => {
            const artistComparison =
              a.tag_data?.artist?.localeCompare(b.tag_data?.artist ?? "") ?? 0;
            if (artistComparison !== 0) return artistComparison;
            const trackComp =
              (a.tag_data?.track_number ?? 0) - (b.tag_data?.track_number ?? 0);
            if (trackComp !== 0) return trackComp;
            return (
              a.tag_data?.title?.localeCompare(b.tag_data?.title ?? "") ?? 0
            );
          })
          .map((song) => ({
            ...(song.tag_data ?? {}),
            song,
          }))}
      />
    </Stack>
  );
}
