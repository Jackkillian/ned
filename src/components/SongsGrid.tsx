import { useLibrary } from "@/contexts/LibraryContext";
import { SimpleGrid, Card, Anchor } from "@mantine/core";
import { useMemo } from "react";
import { Link } from "react-router";
import { AlbumArt } from "./AlbumArt";

export function SongsGrid() {
  const library = useLibrary();
  const songsByAlbum = useMemo(() => library.getSongsByAlbum(), [library]);

  return (
    <SimpleGrid cols={{ base: 1, xs: 3, sm: 4, lg: 5 }} spacing="md">
      {Object.entries(songsByAlbum).map(([album, songs]) => {
        const albumArt = songs[0]?.tag_data?.picture;
        return (
          <Card key={album} shadow="sm" padding="lg" withBorder>
            <Card.Section>
              <AlbumArt albumArt={albumArt} size="fit" />
            </Card.Section>
            <Anchor component={Link} fw={500} mt="md" to={`/album/${album}`}>
              {album}
            </Anchor>
          </Card>
        );
      })}
    </SimpleGrid>
  );
}
