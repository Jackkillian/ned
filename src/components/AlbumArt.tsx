import { AspectRatio, Image, Box, Center } from "@mantine/core";
import { ImageBrokenIcon } from "@phosphor-icons/react";

/**
 * Album art
 *
 * @param props
 * @param props.albumArt Optional album art image source
 */
export function AlbumArt({
  albumArt,
}: {
  albumArt: string | undefined | null;
}) {
  return (
    <AspectRatio ratio={1}>
      {albumArt ? (
        <Image
          radius="md"
          src={albumArt}
          alt="Album Cover"
          draggable="false"
          w="128px"
        />
      ) : (
        <Box bg="dark.6" c="dimmed">
          <Center h="100%">
            <ImageBrokenIcon size={128} />
          </Center>
        </Box>
      )}
    </AspectRatio>
  );
}
