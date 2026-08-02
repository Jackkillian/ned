import { Text, Image, Anchor } from "@mantine/core";
import { DataTable } from "mantine-datatable";
import { emitTo } from "@tauri-apps/api/event";
import { useLibrary } from "@/contexts/LibraryContext";
import { getFileName } from "@/utils";

/**
 * Table view for songs
 */
export function SongsTable() {
  const library = useLibrary();
  const { songs } = library;

  return (
    <DataTable
      columns={[
        {
          accessor: "picture",
          title: "Album Art",
          render: (row) =>
            row.picture && (
              <Image
                radius="md"
                src={row.picture}
                alt="Album Cover"
                draggable="false"
                w="48px"
              />
            ),
        },
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
        { accessor: "album" },
        { accessor: "artist" },
        { accessor: "year" },
        { accessor: "disc_number" },
        { accessor: "track_number" },
      ]}
      records={songs
        .sort((a, b) => {
          const artistComparison =
            a.tag_data?.artist?.localeCompare(b.tag_data?.artist ?? "") ?? 0;
          if (artistComparison !== 0) return artistComparison;
          const albumComparision =
            a.tag_data?.album?.localeCompare(b.tag_data?.album ?? "") ?? 0;
          if (albumComparision !== 0) return artistComparison;
          const trackComp =
            (a.tag_data?.track_number ?? 0) - (b.tag_data?.track_number ?? 0);
          if (trackComp !== 0) return trackComp;
          return a.tag_data?.title?.localeCompare(b.tag_data?.title ?? "") ?? 0;
        })
        .map((song) => ({
          ...(song.tag_data ?? {}),
          song,
        }))}
    />
  );
}
