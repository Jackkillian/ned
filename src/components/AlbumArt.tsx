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
  size,
}: {
  albumArt: string | undefined | null;
  size: string | number;
}) {
  return (
    <AspectRatio ratio={1}>
      {albumArt ? (
        <Image
          radius="md"
          src={albumArt}
          alt="Album Cover"
          draggable="false"
          w={size}
        />
      ) : (
        <Box bg="dark.6" c="dimmed">
          <Center h="100%" p="xl">
            <ImageBrokenIcon size={size === "fit" ? "50%" : size} />
          </Center>
        </Box>
      )}
    </AspectRatio>
  );
}
