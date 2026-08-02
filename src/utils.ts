/**
 * Get the file name from a file path
 *
 * @param path
 */
export function getFileName(path: string) {
  const segments = path.split("/");
  return segments[segments.length - 1];
}
