import { Box, Flex } from "@chakra-ui/react";
import type { ReactNode } from "react";

type BaseCardProps = {
  title: ReactNode;
  body: ReactNode;
  titleBgColor?: string;
  className?: string;
};

export function BaseCard({
  title,
  body,
  titleBgColor = "#000000",
  className,
}: BaseCardProps) {
  return (
    <Box
      display="flex"
      flexDirection="column"
      width="100%"
      overflow="hidden"
      borderRadius="lg"
      border="1px solid"
      borderColor="gray.700"
      className={className}
    >
      <Flex
        alignItems="center"
        justifyContent="space-between"
        px={4}
        py={3}
        bg={titleBgColor}
      >
        <Box fontWeight="bold">{title}</Box>
      </Flex>
      <Flex
        flex={1}
        alignItems="center"
        bg="gray.800"
        p={5}
      >
        {body}
      </Flex>
    </Box>
  );
}
